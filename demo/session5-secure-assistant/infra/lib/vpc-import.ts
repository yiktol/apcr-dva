import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

// Literal VPC attributes from the given exports. We use
// `ec2.Vpc.fromVpcAttributes` (NOT `fromLookup`) so `cdk synth` needs no live
// AWS context lookup and runs fully offline (NFR-4). The six subnet ids and the
// three AZs line up positionally (private[i] and public[i] share AZs[i]).
//
// We NEVER create a VPC — the synthesized template must contain no
// `AWS::EC2::VPC` resource.
const VPC_ID = 'vpc-01857e627d800ca7a';
const VPC_CIDR = '10.1.0.0/16';
const AZS = ['ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c'];

const PRIVATE_SUBNET_IDS = [
  'subnet-031c1ad1112e14559', // 1a
  'subnet-000af0b0c27929d53', // 1b
  'subnet-09bb34168e90ddd6f', // 1c
];

const PUBLIC_SUBNET_IDS = [
  'subnet-05de990ce1677a9b8', // 1a
  'subnet-029d8307a796a725c', // 1b
  'subnet-03bb2e0d84b125eb0', // 1c
];

/**
 * Import the existing VPC by its literal attributes. Returns an `IVpc` with the
 * private + public subnets wired by AZ.
 */
export function importVpc(scope: Construct): ec2.IVpc {
  return ec2.Vpc.fromVpcAttributes(scope, 'ImportedVpc', {
    vpcId: VPC_ID,
    vpcCidrBlock: VPC_CIDR,
    availabilityZones: AZS,
    privateSubnetIds: PRIVATE_SUBNET_IDS,
    publicSubnetIds: PUBLIC_SUBNET_IDS,
    // NOTE: the private subnets carry a NAT route, but the assistant reaches
    // Bedrock ONLY via the bedrock-runtime interface endpoint (see
    // app-edge-ai-stack.ts), never over NAT. "private subnet" does not by
    // itself mean "private path to Bedrock".
  });
}

/**
 * The three private subnets as a `SubnetSelection`, selected explicitly by id
 * (not by subnet-type default) so Lambdas and the interface endpoints land in
 * exactly these subnets.
 */
export function privateSubnetSelection(scope: Construct): ec2.SubnetSelection {
  const subnets = PRIVATE_SUBNET_IDS.map((id, i) =>
    ec2.Subnet.fromSubnetAttributes(scope, `PrivateSubnet${i}`, {
      subnetId: id,
      availabilityZone: AZS[i],
    }),
  );
  return { subnets };
}
