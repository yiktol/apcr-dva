import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';

export interface AppPipelineStackProps extends cdk.StackProps {
  readonly ordersQueue: sqs.Queue;
  readonly ordersTable: dynamodb.Table;
}

/**
 * Application + delivery layer for the coffee-ship demo.
 *
 * ECR repo (keep 10 most recent images), ECS Fargate service behind an ALB,
 * fronted by a CloudFront distribution. The ALB is NOT exposed to the public
 * internet directly: its security group only allows ingress from the AWS
 * managed CloudFront origin-facing prefix list, so only CloudFront can reach
 * it. The VPC is imported from the account's CloudFormation exports (VpcId,
 * PublicSubnetOne/Two/Three) rather than created here. Also: an SNS topic for
 * manual approval, a CloudWatch alarm, and a CodePipeline whose source is a
 * versioned S3 bucket (no GitHub/CodeCommit):
 *   Source (S3 source.zip) -> Build (CodeBuild: docker build/push to ECR +
 *   imagedefinitions.json) -> Deploy-to-test (real ECS rolling deploy) ->
 *   Manual approval (SNS) -> Deploy-to-prod (real ECS rolling deploy).
 *
 * BOOTSTRAP ORDER (chicken-and-egg): the ECR repo is empty until the pipeline
 * runs, but the ECS service needs an image to start. The service references
 * `coffee-ship:latest`, so on the FIRST `cdk deploy` the service task cannot
 * pull an image yet and will NOT stabilize — this is expected. Deploy the
 * stacks, then run the pipeline once (upload source.zip containing container/
 * and container/buildspec.yml). Build pushes `:latest` + a unique tag; the
 * Deploy-to-test ECS action registers a new task def pointing at the unique
 * tag and the service becomes healthy. Approve, and Deploy-to-prod rolls the
 * same service to the approved image.
 */
export class AppPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppPipelineStackProps) {
    super(scope, id, props);

    const { ordersQueue, ordersTable } = props;

    // ---------------------------------------------------------------------
    // Import the EXISTING VPC from the account's CloudFormation exports.
    // We do not create a VPC. Exports used: VpcId, VpcCidrBlock, and the three
    // public subnets (PublicSubnetOne/Two/Three), all published account-wide.
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

    // ---------------------------------------------------------------------
    // ECR repository with a lifecycle rule keeping the 10 most recent images.
    // ---------------------------------------------------------------------
    const repository = new ecr.Repository(this, 'CoffeeShipRepo', {
      repositoryName: 'coffee-ship',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      emptyOnDelete: true,
      lifecycleRules: [
        {
          description: 'Keep only the 10 most recent images',
          maxImageCount: 10,
        },
      ],
    });

    // ---------------------------------------------------------------------
    // ECS Fargate service behind an ALB in the public VPC.
    // ---------------------------------------------------------------------
    const cluster = new ecs.Cluster(this, 'CoffeeShipCluster', {
      vpc,
      clusterName: 'coffee-ship',
    });

    const fargateService = new ecs_patterns.ApplicationLoadBalancedFargateService(
      this,
      'CoffeeShipService',
      {
        cluster,
        serviceName: 'coffee-ship',
        cpu: 256,
        memoryLimitMiB: 512,
        desiredCount: 1,
        assignPublicIp: true,
        taskSubnets: { subnetType: ec2.SubnetType.PUBLIC },
        // The ALB is internet-facing at the network level so CloudFront can
        // reach it, but its security group (below) only admits the CloudFront
        // prefix list, so the public cannot hit it directly.
        publicLoadBalancer: true,
        minHealthyPercent: 100,
        maxHealthyPercent: 200,
        circuitBreaker: { rollback: true },
        // Give tasks time to pass health checks before the circuit breaker judges them.
        healthCheckGracePeriod: cdk.Duration.seconds(120),
        taskImageOptions: {
          // The REAL coffee-ship image, pulled from the ECR repo above. The
          // pipeline's CodeBuild stage builds container/ and pushes `:latest`
          // plus a unique tag; the ECS deploy actions then roll the service to
          // the unique tag via imagedefinitions.json.
          //
          // BOOTSTRAP: on the first `cdk deploy` the ECR repo is empty, so this
          // `:latest` reference cannot be pulled and the service will not
          // stabilize until the pipeline has run once (see the class comment).
          image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
          // Container name is left at the pattern default ("web"); the build's
          // imagedefinitions.json uses "web" so the ECS deploy action matches.
          containerPort: 8080,
          environment: {
            ORDERS_QUEUE_URL: ordersQueue.queueUrl,
            ORDERS_TABLE_NAME: ordersTable.tableName,
          },
        },
      },
    );

    // The ALB health check targets GET / by default (path "/"), which the
    // coffee-ship app answers with {"status":"ok"}; leave the pattern default.

    // Let the task read/write the orders data plane.
    ordersQueue.grantConsumeMessages(fargateService.taskDefinition.taskRole);
    ordersTable.grantReadWriteData(fargateService.taskDefinition.taskRole);
    repository.grantPull(fargateService.taskDefinition.obtainExecutionRole());

    // ---------------------------------------------------------------------
    // Lock the ALB so ONLY CloudFront can reach it.
    //
    // The ApplicationLoadBalancedFargateService opens the ALB security group to
    // 0.0.0.0/0 by default. We strip that and allow ingress only from the AWS
    // managed prefix list "com.amazonaws.global.cloudfront.origin-facing",
    // which contains CloudFront's origin-facing IP ranges. The public internet
    // can therefore only reach the app through CloudFront.
    // ---------------------------------------------------------------------
    const albSg = fargateService.loadBalancer.connections.securityGroups[0];

    // The AWS managed "com.amazonaws.global.cloudfront.origin-facing" prefix
    // list id is region-specific. In ap-southeast-1 it is pl-31a34658. It is
    // exposed as a stack parameter (defaulted to that id) so the id is not
    // silently hard-coded and can be overridden per region at deploy time.
    const cloudFrontPrefixListId = new cdk.CfnParameter(this, 'CloudFrontPrefixListId', {
      type: 'String',
      default: 'pl-31a34658',
      description:
        'AWS managed CloudFront origin-facing prefix list id for this region (ap-southeast-1 = pl-31a34658)',
    });
    const cloudFrontPrefixList = ec2.PrefixList.fromPrefixListId(
      this,
      'CloudFrontOriginFacingPL',
      cloudFrontPrefixListId.valueAsString,
    );

    // Replace the auto-created wide-open (0.0.0.0/0) ingress with a single rule
    // that admits HTTP only from the CloudFront origin-facing prefix list.
    const cfnAlbSg = albSg.node.defaultChild as ec2.CfnSecurityGroup;
    cfnAlbSg.addPropertyOverride('SecurityGroupIngress', [
      {
        Description: 'Allow HTTP only from the CloudFront origin-facing prefix list',
        IpProtocol: 'tcp',
        FromPort: 80,
        ToPort: 80,
        SourcePrefixListId: cloudFrontPrefixList.prefixListId,
      },
    ]);

    // ---------------------------------------------------------------------
    // CloudFront in front of the ALB (ALB is the custom origin over HTTP).
    // ---------------------------------------------------------------------
    const distribution = new cloudfront.Distribution(this, 'CoffeeShipCdn', {
      comment: 'coffee-ship demo: CloudFront in front of the ALB',
      defaultBehavior: {
        origin: new origins.LoadBalancerV2Origin(fargateService.loadBalancer, {
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
      description: 'Public entry point: CloudFront distribution URL (use this, not the ALB)',
    });
    new cdk.CfnOutput(this, 'CloudFrontDistributionId', {
      value: distribution.distributionId,
      description: 'CloudFront distribution id',
    });

    // ---------------------------------------------------------------------
    // SNS topic used for the manual approval step.
    // ---------------------------------------------------------------------
    const approvalTopic = new sns.Topic(this, 'ApprovalTopic', {
      topicName: 'coffee-ship-approval',
      displayName: 'Coffee Ship manual approval notifications',
    });

    // ---------------------------------------------------------------------
    // CloudWatch alarm: ECS service unhealthy host count.
    // ---------------------------------------------------------------------
    new cloudwatch.Alarm(this, 'UnhealthyHostAlarm', {
      alarmName: 'coffee-ship-unhealthy-hosts',
      alarmDescription: 'Alarm when the ALB target group has unhealthy hosts',
      metric: fargateService.targetGroup.metrics.unhealthyHostCount({
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

    const sourceAction = new codepipeline_actions.S3SourceAction({
      actionName: 'S3_Source',
      bucket: sourceBucket,
      bucketKey: 'source.zip',
      output: sourceOutput,
      trigger: codepipeline_actions.S3Trigger.POLL,
    });

    // CodeBuild project driven by the container buildspec. privileged:true so
    // the build can run Docker (docker build + docker push to ECR).
    const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
      projectName: 'coffee-ship-build',
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        privileged: true,
      },
      buildSpec: codebuild.BuildSpec.fromSourceFilename('container/buildspec.yml'),
    });

    // The build pushes images to the coffee-ship ECR repo.
    repository.grantPullPush(buildProject);

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'Build',
      project: buildProject,
      input: sourceOutput,
      outputs: [buildOutput],
    });

    // Real ECS rolling deploy to the single coffee-ship service. The deploy
    // action reads imagedefinitions.json from the build output artifact and
    // registers a new task definition pointing at the freshly built image.
    // EcsDeployAction auto-grants ecs:UpdateService / RegisterTaskDefinition /
    // iam:PassRole etc. to the action role, so no manual IAM policy is needed.
    const deployTestAction = new codepipeline_actions.EcsDeployAction({
      actionName: 'Deploy_To_Test',
      service: fargateService.service,
      input: buildOutput,
    });

    const manualApprovalAction = new codepipeline_actions.ManualApprovalAction({
      actionName: 'Manual_Approval',
      notificationTopic: approvalTopic,
      additionalInformation: 'Approve to promote the coffee-ship build to production.',
    });

    // Deploy-to-prod rolls the SAME single service again to the approved image
    // (one service in this demo). Also a real ECS deploy.
    const deployProdAction = new codepipeline_actions.EcsDeployAction({
      actionName: 'Deploy_To_Prod',
      service: fargateService.service,
      input: buildOutput,
    });

    new codepipeline.Pipeline(this, 'CoffeeShipPipeline', {
      pipelineName: 'coffee-ship',
      stages: [
        { stageName: 'Source', actions: [sourceAction] },
        { stageName: 'Build', actions: [buildAction] },
        { stageName: 'Deploy-Test', actions: [deployTestAction] },
        { stageName: 'Approval', actions: [manualApprovalAction] },
        { stageName: 'Deploy-Prod', actions: [deployProdAction] },
      ],
    });
  }
}
