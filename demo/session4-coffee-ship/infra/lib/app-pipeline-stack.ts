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

export interface AppPipelineStackProps extends cdk.StackProps {
  readonly vpc: ec2.Vpc;
  readonly ordersQueue: sqs.Queue;
  readonly ordersTable: dynamodb.Table;
}

/**
 * Application + delivery layer for the coffee-ship demo.
 *
 * ECR repo (keep 10 most recent images), ECS Fargate service behind an ALB in
 * the public VPC, an SNS topic for manual approval, CloudWatch alarms, and a
 * CodePipeline whose source is a versioned S3 bucket (no GitHub/CodeCommit):
 * Source -> Build -> Deploy-to-test -> Manual approval (SNS) -> Deploy-to-prod.
 */
export class AppPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppPipelineStackProps) {
    super(scope, id, props);

    const { vpc, ordersQueue, ordersTable } = props;

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
        publicLoadBalancer: true,
        minHealthyPercent: 100,
        maxHealthyPercent: 200,
        circuitBreaker: { rollback: true },
        taskImageOptions: {
          // Placeholder image until the pipeline publishes to the ECR repo.
          image: ecs.ContainerImage.fromRegistry('public.ecr.aws/amazonlinux/amazonlinux:2023'),
          containerPort: 8080,
          environment: {
            ORDERS_QUEUE_URL: ordersQueue.queueUrl,
            ORDERS_TABLE_NAME: ordersTable.tableName,
          },
        },
      },
    );

    // Let the task read/write the orders data plane.
    ordersQueue.grantConsumeMessages(fargateService.taskDefinition.taskRole);
    ordersTable.grantReadWriteData(fargateService.taskDefinition.taskRole);
    repository.grantPull(fargateService.taskDefinition.obtainExecutionRole());

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
    // CodePipeline: S3 source -> CodeBuild -> deploy-test -> approval -> prod.
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

    // CodeBuild project driven by the app buildspec (app/buildspec.yml).
    const buildProject = new codebuild.PipelineProject(this, 'BuildProject', {
      projectName: 'coffee-ship-build',
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        privileged: true,
      },
      buildSpec: codebuild.BuildSpec.fromSourceFilename('app/buildspec.yml'),
    });

    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'Build',
      project: buildProject,
      input: sourceOutput,
      outputs: [buildOutput],
    });

    const deployTestAction = new codepipeline_actions.S3DeployAction({
      actionName: 'Deploy_To_Test',
      bucket: sourceBucket,
      input: buildOutput,
      objectKey: 'deploy/test',
    });

    const manualApprovalAction = new codepipeline_actions.ManualApprovalAction({
      actionName: 'Manual_Approval',
      notificationTopic: approvalTopic,
      additionalInformation: 'Approve to promote the coffee-ship build to production.',
    });

    const deployProdAction = new codepipeline_actions.S3DeployAction({
      actionName: 'Deploy_To_Prod',
      bucket: sourceBucket,
      input: buildOutput,
      objectKey: 'deploy/prod',
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
