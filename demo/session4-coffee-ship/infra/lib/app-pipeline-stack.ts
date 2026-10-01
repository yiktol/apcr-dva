import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as events from 'aws-cdk-lib/aws-events';
import * as events_targets from 'aws-cdk-lib/aws-events-targets';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as codedeploy from 'aws-cdk-lib/aws-codedeploy';

export interface AppPipelineStackProps extends cdk.StackProps {
  readonly ordersQueue: sqs.Queue;
  readonly ordersTable: dynamodb.Table;
  readonly loyaltyParam: ssm.StringParameter;
  readonly repository: ecr.Repository;
}

/**
 * Application + delivery layer for the coffee-shop app.
 *
 * ECR repo (keep 10 most recent images) and TWO separate ECS environments:
 *   - TEST  (cluster coffee-shop-test): an ApplicationLoadBalancedFargateService
 *     deployed by a standard rolling EcsDeployAction (deployment circuit breaker
 *     + rollback). Fronted by its own ALB + CloudFront distribution.
 *   - PROD  (cluster coffee-shop-prod): a FargateService whose deploymentController
 *     is CODE_DEPLOY, fronted by its own ALB with TWO target groups (blue/green)
 *     and TWO listeners (80 prod + 8080 test/replacement), driven by a real
 *     CodeDeploy ECS blue/green deployment group (canary 10%/5min, auto-rollback
 *     on deployment failure and on a CloudWatch alarm). Fronted by its own
 *     CloudFront distribution (prod origin).
 *
 * Also: an SNS topic for manual approval, per-environment CloudWatch alarms, and
 * a CodePipeline whose source is a versioned S3 bucket:
 *   Source (S3 source.zip) -> Build (CodeBuild: docker build/push to ECR +
 *   imagedefinitions.json + taskdef.json + appspec.yaml) ->
 *   Deploy-Test (rolling EcsDeployAction, coffee-shop-test) ->
 *   Manual approval (SNS) ->
 *   Deploy-Prod (CodeDeployEcsDeployAction, blue/green, coffee-shop-prod).
 *
 * BOOTSTRAP ORDER (chicken-and-egg): the ECR repo is empty until the pipeline
 * runs, but both ECS services need an image to start. Both services reference
 * `coffee-shop:latest`, so on the FIRST `cdk deploy` the service tasks cannot
 * pull an image yet and will NOT stabilize — this is expected. Deploy the
 * stacks, seed ECR `:latest` (deploy.sh) so the prod service has a stable blue
 * task set, then run the pipeline once (upload source.zip containing container/
 * and container/buildspec.yml). Build pushes `:latest` + a unique tag; Deploy-Test
 * rolls the test service to the unique tag; after approval Deploy-Prod runs the
 * first CodeDeploy blue/green deployment against the prod service.
 */
export class AppPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppPipelineStackProps) {
    super(scope, id, props);

    const { ordersQueue, ordersTable, repository } = props;

    // ---------------------------------------------------------------------
    // Reference the VPC via CloudFormation exports: VpcId, VpcCidrBlock, and the
    // three public subnets (PublicSubnetOne/Two/Three), all published
    // account-wide.
    // ---------------------------------------------------------------------
    // PublicSubnetOne/Two/Three live in ap-southeast-1a/1b/1c respectively; the
    // availabilityZones array must line up positionally with publicSubnetIds.
    const vpc = ec2.Vpc.fromVpcAttributes(this, 'ImportedVpc', {
      vpcId: cdk.Fn.importValue('VpcId'),
      vpcCidrBlock: cdk.Fn.importValue('VpcCidrBlock'),
      availabilityZones: ['ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c'],
      publicSubnetIds: [
        cdk.Fn.importValue('PublicSubnetOne'),
        cdk.Fn.importValue('PublicSubnetTwo'),
        cdk.Fn.importValue('PublicSubnetThree'),
      ],
    });

    // The ECR repository (keep-10 lifecycle) is defined in NetworkDataStack and
    // passed in via props, so it exists and can be seeded with an image BEFORE
    // the ECS services below (which pull 'coffee-shop:latest') are created.

    // ---------------------------------------------------------------------
    // Two SEPARATE ECS clusters so the test/prod split is explicit.
    // ---------------------------------------------------------------------
    const testCluster = new ecs.Cluster(this, 'CoffeeShopTestCluster', {
      vpc,
      clusterName: 'coffee-shop-test',
    });
    const prodCluster = new ecs.Cluster(this, 'CoffeeShopProdCluster', {
      vpc,
      clusterName: 'coffee-shop-prod',
    });

    // ---------------------------------------------------------------------
    // Shared CloudFront origin-facing prefix list.
    //
    // The AWS managed "com.amazonaws.global.cloudfront.origin-facing" prefix
    // list id is region-specific. In ap-southeast-1 it is pl-31a34658. It is
    // exposed as a stack parameter (defaulted to that id) so the id is not
    // silently hard-coded and can be overridden per region at deploy time.
    // ---------------------------------------------------------------------
    const cloudFrontPrefixListId = new cdk.CfnParameter(this, 'CloudFrontPrefixListId', {
      type: 'String',
      default: 'pl-31a34658',
      description:
        'CloudFront origin-facing prefix list id for this region (ap-southeast-1 = pl-31a34658)',
    });
    const cloudFrontPrefixList = ec2.PrefixList.fromPrefixListId(
      this,
      'CloudFrontOriginFacingPL',
      cloudFrontPrefixListId.valueAsString,
    );

    // =====================================================================
    // TEST environment: ApplicationLoadBalancedFargateService (rolling deploy).
    // =====================================================================
    const testService = new ecs_patterns.ApplicationLoadBalancedFargateService(
      this,
      'CoffeeShopTestService',
      {
        cluster: testCluster,
        serviceName: 'coffee-shop-test',
        cpu: 256,
        memoryLimitMiB: 512,
        desiredCount: 1,
        assignPublicIp: true,
        taskSubnets: { subnetType: ec2.SubnetType.PUBLIC },
        publicLoadBalancer: true,
        minHealthyPercent: 100,
        maxHealthyPercent: 200,
        circuitBreaker: { rollback: true },
        // Give tasks time to pass health checks before the circuit breaker judges them.
        healthCheckGracePeriod: cdk.Duration.seconds(120),
        taskImageOptions: {
          // The coffee-shop image, pulled from the ECR repo above. The
          // pipeline's CodeBuild stage builds container/ and pushes `:latest`
          // plus a unique tag; the rolling EcsDeployAction then rolls this test
          // service to the unique tag via imagedefinitions.json.
          //
          // BOOTSTRAP: on the first `cdk deploy` the ECR repo is empty, so this
          // `:latest` reference cannot be pulled and the service will not
          // stabilize until the pipeline has run once (see the class comment).
          image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
          // Container name made EXPLICIT: the test imagedefinitions.json
          // (name:"web") and the prod taskdef.json / appspec.yaml all reference
          // "web", so pin it here so a future CDK default change cannot drift it.
          containerName: 'web',
          containerPort: 8080,
          environment: {
            ORDERS_QUEUE_URL: ordersQueue.queueUrl,
            ORDERS_TABLE_NAME: ordersTable.tableName,
          },
        },
      },
    );

    // The ALB health check targets GET / by default (path "/"), which the
    // coffee-shop app answers at HTTP 200; leave the pattern default.

    // Let the test task read/write the orders data plane.
    ordersQueue.grantConsumeMessages(testService.taskDefinition.taskRole);
    ordersTable.grantReadWriteData(testService.taskDefinition.taskRole);
    props.loyaltyParam.grantRead(testService.taskDefinition.taskRole);
    repository.grantPull(testService.taskDefinition.obtainExecutionRole());

    // ---------------------------------------------------------------------
    // Set the TEST ALB security group ingress.
    //
    // The ApplicationLoadBalancedFargateService opens the ALB security group to
    // 0.0.0.0/0 by default. We replace that rule with ingress from the AWS
    // managed prefix list "com.amazonaws.global.cloudfront.origin-facing".
    // ---------------------------------------------------------------------
    const testAlbSg = testService.loadBalancer.connections.securityGroups[0];
    const cfnTestAlbSg = testAlbSg.node.defaultChild as ec2.CfnSecurityGroup;
    cfnTestAlbSg.addPropertyOverride('SecurityGroupIngress', [
      {
        Description: 'Allow HTTP from the CloudFront origin-facing prefix list',
        IpProtocol: 'tcp',
        FromPort: 80,
        ToPort: 80,
        SourcePrefixListId: cloudFrontPrefixList.prefixListId,
      },
    ]);

    // =====================================================================
    // PROD environment: FargateService with CODE_DEPLOY controller + blue/green
    // ALB (two target groups, two listeners), driven by CodeDeploy canary.
    // =====================================================================
    const prodAlb = new elbv2.ApplicationLoadBalancer(this, 'CoffeeShopProdAlb', {
      vpc,
      internetFacing: true,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
    });

    const prodBlueTg = new elbv2.ApplicationTargetGroup(this, 'ProdBlueTg', {
      vpc,
      port: 8080,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      // NIT finding 5: the health-check path '/' returns HTTP 200 from app.py
      // even in degraded (unbaked SPA) mode — it gates task LIVENESS, not SPA
      // correctness. A broken SPA still passes this check; that is intentional
      // (a crashed process is what we want to catch here).
      healthCheck: { path: '/', healthyHttpCodes: '200' },
      deregistrationDelay: cdk.Duration.seconds(10),
    });
    const prodGreenTg = new elbv2.ApplicationTargetGroup(this, 'ProdGreenTg', {
      vpc,
      port: 8080,
      protocol: elbv2.ApplicationProtocol.HTTP,
      targetType: elbv2.TargetType.IP,
      // NIT finding 5 (same as blue): '/' returns 200 even degraded — liveness,
      // not SPA correctness. The green task set's own health check still gates
      // the CodeDeploy traffic shift.
      healthCheck: { path: '/', healthyHttpCodes: '200' },
      deregistrationDelay: cdk.Duration.seconds(10),
    });

    // Production listener (port 80) — serves live traffic, starts on blue.
    // CRITICAL: open:false. addListener defaults open:true
    // (ApplicationListenerProps.open @default true), which would auto-add a
    // 0.0.0.0/0 ingress rule on the ALB SG for the listener port. We disable the
    // auto-open and add the prefix-list rule ourselves (below).
    const prodListener = prodAlb.addListener('ProdListener', {
      port: 80,
      protocol: elbv2.ApplicationProtocol.HTTP,
      open: false,
      defaultTargetGroups: [prodBlueTg],
    });
    // Test/replacement listener (port 8080) — CodeDeploy shifts the replacement
    // (green) task set here during its blue/green orchestration. open:false for
    // the same reason; port 8080 gets no internet ingress at all because nothing
    // external probes green here (no BeforeAllowTraffic / AfterAllowTestTraffic
    // hooks).
    const prodTestListener = prodAlb.addListener('ProdTestListener', {
      port: 8080,
      protocol: elbv2.ApplicationProtocol.HTTP,
      open: false,
      defaultTargetGroups: [prodGreenTg],
    });

    const prodTaskDef = new ecs.FargateTaskDefinition(this, 'ProdTaskDef', {
      family: 'coffee-shop-prod',
      cpu: 256,
      memoryLimitMiB: 512,
    });
    // Explicit log group named exactly '/ecs/coffee-shop-prod' so it MATCHES the
    // awslogs-group hard-coded in the CodeDeploy-registered container/taskdef.json.
    // Using an explicit log group here makes CDK grant the prod task EXECUTION
    // role logs:CreateLogStream/PutLogEvents on THIS group — without it the
    // CodeDeploy green task fails to start (TaskFailedToStart: not authorized to
    // CreateLogStream on /ecs/coffee-shop-prod), stalling the blue/green shift.
    const prodLogGroup = new logs.LogGroup(this, 'ProdLogGroup', {
      logGroupName: '/ecs/coffee-shop-prod',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
    const prodContainer = prodTaskDef.addContainer('web', {
      image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'coffee-shop-prod', logGroup: prodLogGroup }),
      environment: {
        ORDERS_QUEUE_URL: ordersQueue.queueUrl,
        ORDERS_TABLE_NAME: ordersTable.tableName,
      },
    });
    prodContainer.addPortMappings({ containerPort: 8080, protocol: ecs.Protocol.TCP });

    const prodService = new ecs.FargateService(this, 'CoffeeShopProdService', {
      cluster: prodCluster,
      serviceName: 'coffee-shop-prod',
      taskDefinition: prodTaskDef,
      desiredCount: 1,
      assignPublicIp: true,
      vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
      minHealthyPercent: 100,
      maxHealthyPercent: 200,
      healthCheckGracePeriod: cdk.Duration.seconds(120),
      deploymentController: { type: ecs.DeploymentControllerType.CODE_DEPLOY },
    });
    // Register the prod service with the BLUE target group only; CodeDeploy
    // manages registration into green during a deployment.
    //
    // NIT finding 4: attachToApplicationTargetGroup adds only task-SG ingress
    // FROM the ALB to the task port — it does NOT add any listener/world
    // ingress to the ALB SG. The internet-facing ingress on the prod ALB SG is
    // controlled solely by the explicit allowDefaultPortFrom(prefix list) below,
    // and the synth-time "no 0.0.0.0/0 on the prod ALB SG" check covers it.
    prodService.attachToApplicationTargetGroup(prodBlueTg);

    // Prod data-plane grants (same shape as test) + ECR pull on the exec role.
    ordersQueue.grantConsumeMessages(prodTaskDef.taskRole);
    ordersTable.grantReadWriteData(prodTaskDef.taskRole);
    props.loyaltyParam.grantRead(prodTaskDef.taskRole);
    repository.grantPull(prodTaskDef.obtainExecutionRole());

    // Prod unhealthy-host alarm (wired into CodeDeploy auto-rollback). We alarm
    // on BLUE (the stable live task set), not green, to avoid a false rollback
    // during the normal green-registration window. evaluationPeriods 1 so a
    // prod regression trips rollback fast (NIT finding 3: distinct from the
    // informational test alarm's 2 periods).
    const prodUnhealthyHostAlarm = new cloudwatch.Alarm(this, 'ProdUnhealthyHostAlarm', {
      alarmName: 'coffee-shop-prod-unhealthy-hosts',
      alarmDescription: 'Alarm when the prod (blue) ALB target group has unhealthy hosts',
      metric: prodBlueTg.metrics.unhealthyHostCount({
        period: cdk.Duration.minutes(1),
        statistic: cloudwatch.Stats.MAXIMUM,
      }),
      threshold: 1,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    // CodeDeploy ECS blue/green: canary 10% every 5 minutes, auto-rollback on
    // deployment failure AND on the prod alarm.
    const prodDeployApp = new codedeploy.EcsApplication(this, 'ProdCodeDeployApp', {
      applicationName: 'coffee-shop-prod',
    });
    const prodDeployGroup = new codedeploy.EcsDeploymentGroup(this, 'ProdDeployGroup', {
      application: prodDeployApp,
      deploymentGroupName: 'coffee-shop-prod',
      service: prodService,
      blueGreenDeploymentConfig: {
        blueTargetGroup: prodBlueTg,
        greenTargetGroup: prodGreenTg,
        listener: prodListener,
        testListener: prodTestListener,
        // Keep the old (blue) task set 10 min after a successful shift so a
        // manual console rollback is possible without a full redeploy.
        terminationWaitTime: cdk.Duration.minutes(10),
      },
      deploymentConfig: codedeploy.EcsDeploymentConfig.CANARY_10PERCENT_5MINUTES,
      autoRollback: { failedDeployment: true, deploymentInAlarm: true },
      alarms: [prodUnhealthyHostAlarm],
    });

    // Prod ALB ingress: the prod listener (port 80) from the CloudFront prefix
    // list. Port 8080 (CodeDeploy test listener) is left with no internet
    // ingress at all.
    prodListener.connections.allowDefaultPortFrom(
      ec2.Peer.prefixList(cloudFrontPrefixList.prefixListId),
      'CloudFront prod listener',
    );

    // ---------------------------------------------------------------------
    // CloudFront in front of the PROD ALB (ALB is the custom origin over HTTP).
    // ---------------------------------------------------------------------
    const distribution = new cloudfront.Distribution(this, 'CoffeeShopCdn', {
      comment: 'coffee-shop: CloudFront in front of the PROD ALB',
      defaultBehavior: {
        origin: new origins.LoadBalancerV2Origin(prodAlb, {
          protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY,
          httpPort: 80,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
        originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
      },
    });

    new cdk.CfnOutput(this, 'CloudFrontUrl', {
      value: `https://${distribution.distributionDomainName}`,
      description: 'Public entry point (PROD): CloudFront distribution URL (use this, not the ALB)',
    });
    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: distribution.distributionId,
      description: 'CloudFront distribution id (prod)',
    });

    // ---------------------------------------------------------------------
    // Second CloudFront distribution in front of the TEST ALB, so a
    // reviewer can see the TEST environment in a browser. Mirrors the prod
    // distribution config exactly (CACHING_DISABLED + ALL_VIEWER + HTTP_ONLY
    // origin) so the SPA's same-origin API calls work unchanged.
    // ---------------------------------------------------------------------
    const testCdn = new cloudfront.Distribution(this, 'CoffeeShopTestCdn', {
      comment: 'coffee-shop: CloudFront in front of the TEST ALB',
      defaultBehavior: {
        origin: new origins.LoadBalancerV2Origin(testService.loadBalancer, {
          protocolPolicy: cloudfront.OriginProtocolPolicy.HTTP_ONLY,
          httpPort: 80,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
        originRequestPolicy: cloudfront.OriginRequestPolicy.ALL_VIEWER,
      },
    });

    new cdk.CfnOutput(this, 'TestCloudFrontUrl', {
      value: `https://${testCdn.distributionDomainName}`,
      description: 'Public entry point (TEST): CloudFront distribution URL for the test environment',
    });

    // ---------------------------------------------------------------------
    // SNS topic used for the manual approval step.
    // ---------------------------------------------------------------------
    const approvalTopic = new sns.Topic(this, 'ApprovalTopic', {
      topicName: 'coffee-shop-approval',
      displayName: 'Coffee Shop manual approval notifications',
    });

    // ---------------------------------------------------------------------
    // CloudWatch alarm: TEST ECS service unhealthy host count.
    //
    // NIT finding 3: this is the TEST alarm and is purely INFORMATIONAL — it is
    // NOT wired into any rollback (the test service already rolls back via its
    // deployment circuit breaker). It intentionally keeps evaluationPeriods 2;
    // only the prod alarm (evaluationPeriods 1, wired into CodeDeploy
    // auto-rollback) is normalized to react fast. Do NOT align these two.
    // ---------------------------------------------------------------------
    new cloudwatch.Alarm(this, 'UnhealthyHostAlarm', {
      alarmName: 'coffee-shop-test-unhealthy-hosts',
      alarmDescription: 'Informational: TEST ALB target group has unhealthy hosts',
      metric: testService.targetGroup.metrics.unhealthyHostCount({
        period: cdk.Duration.minutes(1),
        statistic: cloudwatch.Stats.MAXIMUM,
      }),
      threshold: 1,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
      treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
    });

    // ---------------------------------------------------------------------
    // CodePipeline: S3 source -> CodeBuild (docker) -> ECS deploy (test) ->
    // manual approval -> ECS deploy (prod). The source zip must contain the
    // container/ directory and container/buildspec.yml.
    // ---------------------------------------------------------------------
    const sourceBucket = new s3.Bucket(this, 'SourceBucket', {
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
    });

    const sourceOutput = new codepipeline.Artifact('SourceArtifact');
    const buildOutput = new codepipeline.Artifact('BuildArtifact');

    // Trigger exactly ONCE per source.zip write via the native S3 -> EventBridge
    // "Object Created" notification (wired explicitly below). We deliberately do
    // NOT use S3Trigger.POLL (polling can start a second, overlapping execution
    // that races the first on the single ECS service — one wins, the other
    // fails its ECS deploy) and NOT S3Trigger.EVENTS (that builds a CloudTrail
    // "AWS API Call" rule which needs S3 data-event logging to exist). Using
    // S3Trigger.NONE + an explicit EventBridge rule is deterministic and needs
    // no CloudTrail: one upload => one execution.
    sourceBucket.enableEventBridgeNotification();

    const sourceAction = new codepipeline_actions.S3SourceAction({
      actionName: 'S3_Source',
      bucket: sourceBucket,
      bucketKey: 'source.zip',
      output: sourceOutput,
      trigger: codepipeline_actions.S3Trigger.NONE,
    });

    // CodeBuild project driven by the container buildspec. privileged:true so
    // the build can run Docker (docker build + docker push to ECR).
    const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
      projectName: 'coffee-shop-build',
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        privileged: true,
      },
      // These keys MUST match the buildspec (FEAT-002): the post_build sed
      // renders container/taskdef.json into the artifact-root taskdef.json,
      // substituting <EXECUTION_ROLE_ARN>/<TASK_ROLE_ARN>/<ORDERS_QUEUE_URL>
      // from these env vars (and guards all three are non-empty).
      environmentVariables: {
        PROD_EXECUTION_ROLE_ARN: {
          value: prodTaskDef.obtainExecutionRole().roleArn,
        },
        PROD_TASK_ROLE_ARN: {
          value: prodTaskDef.taskRole.roleArn,
        },
        ORDERS_QUEUE_URL: {
          value: ordersQueue.queueUrl,
        },
      },
      buildSpec: codebuild.BuildSpec.fromSourceFilename('container/buildspec.yml'),
    });

    // The build pushes images to the coffee-shop ECR repo.
    repository.grantPullPush(buildProject);

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'Build',
      project: buildProject,
      input: sourceOutput,
      outputs: [buildOutput],
    });

    // Real ECS ROLLING deploy to the coffee-shop-test service. The deploy
    // action reads imagedefinitions.json from the build output artifact and
    // registers a new task definition pointing at the freshly built image.
    // EcsDeployAction auto-grants ecs:UpdateService / RegisterTaskDefinition /
    // iam:PassRole etc. to the action role, so no manual IAM policy is needed.
    const deployTestAction = new codepipeline_actions.EcsDeployAction({
      actionName: 'Deploy_To_Test',
      service: testService.service,
      input: buildOutput,
    });

    const manualApprovalAction = new codepipeline_actions.ManualApprovalAction({
      actionName: 'Manual_Approval',
      notificationTopic: approvalTopic,
      additionalInformation: 'Approve to promote the coffee-shop build to production.',
    });

    // Deploy-to-prod is a REAL CodeDeploy ECS blue/green deployment to the
    // coffee-shop-prod service. It reads appspec.yaml + taskdef.json from the
    // build artifact root and resolves the <IMAGE1_NAME> placeholder in the
    // taskdef from imageDetails.json ({ImageURI}) via containerImageInputs.
    // CodeDeployEcsDeployAction grants the pipeline action role the
    // codedeploy:*, ecs:RegisterTaskDefinition and iam:PassRole it needs.
    const deployProdAction = new codepipeline_actions.CodeDeployEcsDeployAction({
      actionName: 'Deploy_To_Prod',
      deploymentGroup: prodDeployGroup,
      appSpecTemplateInput: buildOutput,
      taskDefinitionTemplateInput: buildOutput,
      containerImageInputs: [
        {
          input: buildOutput,
          taskDefinitionPlaceholder: 'IMAGE1_NAME',
        },
      ],
    });

    const pipeline = new codepipeline.Pipeline(this, 'CoffeeShopPipeline', {
      pipelineName: 'coffee-shop',
      stages: [
        { stageName: 'Source', actions: [sourceAction] },
        { stageName: 'Build', actions: [buildAction] },
        { stageName: 'Deploy-Test', actions: [deployTestAction] },
        { stageName: 'Approval', actions: [manualApprovalAction] },
        { stageName: 'Deploy-Prod', actions: [deployProdAction] },
      ],
    });

    // Start the pipeline on the native S3 "Object Created" event for source.zip.
    // One write => one event => one execution. No CloudTrail, no polling.
    new events.Rule(this, 'SourceZipCreatedRule', {
      description: 'Start the coffee-shop pipeline when source.zip is created in the source bucket',
      eventPattern: {
        source: ['aws.s3'],
        detailType: ['Object Created'],
        detail: {
          bucket: { name: [sourceBucket.bucketName] },
          object: { key: ['source.zip'] },
        },
      },
      targets: [new events_targets.CodePipeline(pipeline)],
    });
  }
}
