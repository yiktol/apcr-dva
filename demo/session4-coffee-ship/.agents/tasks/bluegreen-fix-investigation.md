# Blue/Green Deploy Failure — Root Cause & Fix

## Summary answer

The Deploy-Prod `CodeDeployToECS` action fails with `ConfigurationError` /
`Exception while trying to read the image artifact file from: BuildArtifact`
because of a **single-character filename mismatch**:

- The CodeBuild buildspec writes the image file as **`imageDetails.json`** (plural "Details").
- The AWS Amazon ECS blue/green (`CodeDeployToECS`) action requires the image
  file to be named exactly **`imageDetail.json`** (singular "Detail").

The `Image1ArtifactName` config (`BuildArtifact`) is correct, and the artifact
*does* contain an image file at its root — but it has the wrong name, so the
CodePipeline job worker for `CodeDeployToECS` cannot find `imageDetail.json` and
throws immediately, before any CodeDeploy deployment is created. This perfectly
matches the observed symptom (`aws deploy list-deployments` is empty — the
failure is in the CodePipeline action's artifact reading, not in CodeDeploy).

**The fix is a one-word rename:** change every `imageDetails.json` to
`imageDetail.json` in `container/buildspec.yml`. No CDK change is required
(the CDK wiring and generated CloudFormation are already correct). Everything
else — the `<IMAGE1_NAME>` token, `Image1ContainerName`, the single-artifact
wiring, the appspec/taskdef filenames — is correct.

---

## Evidence

### 1. Official AWS requirement: the file MUST be named `imageDetail.json`

From the AWS CodePipeline "Image definitions file reference"
([file-reference.html](https://docs.aws.amazon.com/codepipeline/latest/userguide/file-reference.html)),
section "imageDetail.json file for Amazon ECS blue/green deployment actions":

- Amazon ECS blue/green deployments require an `imageDetail.json` file as input
  to the deploy action.
- The documentation states as a Note that the name of the file must be
  `imageDetail.json`.
- The documented buildspec snippet is `printf '{"ImageURI":"image_URI"}' > imageDetail.json`
  and the artifact entry is `- imageDetail.json`.

Note the contrast the same doc draws: the *standard* (rolling) ECS deploy uses
`imagedefinitions.json`, while the *blue/green* deploy uses `imageDetail.json`
(singular). The two action types use different file names, which is exactly the
trap this project fell into.

Content was rephrased for compliance with licensing restrictions.

Corroborating community reports of the identical error string
(`Exception while trying to read the image artifact file from ... BuildArtifact`)
converge on the same cause — the blue/green action needs `imageDetail.json`:
[SO 62037921](https://stackoverflow.com/q/62037921),
[SO 55301284](https://stackoverflow.com/questions/55301284/how-to-get-a-built-docker-image-within-a-codepipeline-to-the-deploy-step-with-bl),
[SO 59210366](https://stackoverflow.com/questions/59210366/aws-codepipeline-with-ecs-blue-green-deployment-fails-with-internal-error-take).

### 2. The buildspec writes the WRONG filename

`container/buildspec.yml`, `post_build` phase:

```yaml
# imageDetails.json: {ImageURI} shape consumed by the prod CodeDeploy ECS
# blue/green action to fill the taskdef.json <IMAGE1_NAME> placeholder.
- echo "Writing imageDetails.json (prod CodeDeploy blue/green)..."
- printf '{"ImageURI":"%s"}' "$REPO_URI:$IMAGE_TAG" > imageDetails.json
```

and in `artifacts.files`:

```yaml
artifacts:
  files:
    - imagedefinitions.json
    - imageDetails.json      # <-- WRONG: must be imageDetail.json
    - taskdef.json
    - appspec.yaml
```

The JSON *content* is correct (`{"ImageURI":"<ecr>:<tag>"}`). Only the
**filename** is wrong: `imageDetails.json` instead of `imageDetail.json`.
The `cat` line at the end of `post_build` also references `imageDetails.json`.

### 3. The CDK wiring and generated CloudFormation are CORRECT

`infra/lib/app-pipeline-stack.ts` — the action is wired as:

```ts
new codepipeline_actions.CodeDeployEcsDeployAction({
  actionName: 'Deploy_To_Prod',
  deploymentGroup: prodDeployGroup,
  appSpecTemplateInput: buildOutput,
  taskDefinitionTemplateInput: buildOutput,
  containerImageInputs: [{ input: buildOutput, taskDefinitionPlaceholder: 'IMAGE1_NAME' }],
});
```

Synthesized CloudFormation for the `Deploy_To_Prod` action
(`cd infra && cdk synth CoffeeShipAppPipeline`), Configuration block:

```yaml
Provider: CodeDeployToECS
Configuration:
  ApplicationName:        { Ref: ProdCodeDeployApp... }
  DeploymentGroupName:    { Ref: ProdDeployGroup... }
  TaskDefinitionTemplateArtifact: BuildArtifact
  TaskDefinitionTemplatePath:     taskdef.json
  AppSpecTemplateArtifact:        BuildArtifact
  AppSpecTemplatePath:            appspec.yaml
  Image1ArtifactName:             BuildArtifact
  Image1ContainerName:            IMAGE1_NAME
InputArtifacts:
  - Name: BuildArtifact
```

This is exactly what AWS expects:

- `Image1ArtifactName: BuildArtifact` names the artifact that must contain the
  image file. Correct — the build artifact is where the file lives.
- `Image1ContainerName: IMAGE1_NAME` is the placeholder token name. CodeDeploy
  wraps it in angle brackets and replaces `<IMAGE1_NAME>` in the task
  definition. Correct (see item 4).
- `TaskDefinitionTemplatePath: taskdef.json` / `AppSpecTemplatePath: appspec.yaml`
  are the CDK defaults and match the files the build emits. Correct.

Note on terminology: the `CodeDeployToECS` provider has **no configuration key
for the image file name** — the image file name is *not* configurable and is
hard-required by the provider to be `imageDetail.json` at the artifact root.
That is why there is no CDK property to "fix" this and why the only correct fix
is to rename the file the build produces.

### 4. The CDK source confirms the mapping (and that there is no filename knob)

`infra/node_modules/aws-cdk-lib/aws-codepipeline-actions/lib/codedeploy/ecs-deploy-action.js`
(v2.160.0), in `bound()`:

```js
for (let i = 1; i <= containerImageInputs.length; i++) {
  const imageInput = containerImageInputs[i - 1];
  actionConfig.configuration[`Image${i}ArtifactName`] =
    Lazy.string({ produce: () => imageInput.input.artifactName });
  actionConfig.configuration[`Image${i}ContainerName`] =
    imageInput.taskDefinitionPlaceholder ? imageInput.taskDefinitionPlaceholder : 'IMAGE';
}
```

So `containerImageInputs[0]` produces:
- `Image1ArtifactName` = the input artifact's name (`BuildArtifact`).
- `Image1ContainerName` = `taskDefinitionPlaceholder` (`IMAGE1_NAME`).

The construct emits only `TaskDefinitionTemplatePath` and `AppSpecTemplatePath`
as path configuration; it emits **no image-file path** key. The image file name
is fixed by the service to `imageDetail.json`. The `.d.ts` doc for
`CodeDeployEcsContainerImageInput.input` likewise states the artifact's
`imageDetails.json`... — note the CDK *doc comment* itself has the wrong name,
but the comment is advisory; the **service** enforces `imageDetail.json`. This
documentation inconsistency in CDK is very likely what led to the bug.

### 5. The `<IMAGE1_NAME>` token matches `IMAGE1_NAME` (confirmed, no change needed)

`container/taskdef.json` container definition:

```json
{ "name": "web", "image": "<IMAGE1_NAME>", "essential": true, ... }
```

CodeDeploy replaces the placeholder named by `taskDefinitionPlaceholder`
(`IMAGE1_NAME`) wrapped in angle brackets, i.e. it substitutes `<IMAGE1_NAME>`
with the `ImageURI` read from `imageDetail.json`. The token in the committed
`taskdef.json` is exactly `<IMAGE1_NAME>`. **This is correct.** (It only ever
gets exercised *after* the image file is read, so it was never the cause of the
immediate failure.)

### 6. Using one artifact for all three inputs is supported (not the cause)

`appSpecTemplateInput`, `taskDefinitionTemplateInput`, and
`containerImageInputs[].input` all referencing the same `buildOutput`
(`BuildArtifact`) is a supported pattern — the action simply needs each named
file (`appspec.yaml`, `taskdef.json`, `imageDetail.json`) to exist at the root
of that artifact. The `appspec.yaml` has `<TASK_DEFINITION>` (correct, CodeDeploy
fills it) and no image placeholder (correct — the image is injected into the
task def, not the appspec). The single-artifact wiring is **not** the problem.

---

## Conclusion

Root cause: the build artifact contains `imageDetails.json` but the
`CodeDeployToECS` blue/green action requires the file to be named
`imageDetail.json`. The action cannot find the required file in `BuildArtifact`
and fails with `ConfigurationError` before creating any CodeDeploy deployment —
exactly the observed behavior.

This is a filename mismatch (case (a) in the brief's question 1), specifically
the singular-vs-plural `imageDetail` vs `imageDetails`. It is **not**:
- (b) reusing one artifact for all three inputs — that is supported;
- (c) a missing/empty `Image1ContainerName` — it is correctly `IMAGE1_NAME`;
- (d) wrong appspec/taskdef default filenames — those are correct;
- a CDK synth defect — the generated CloudFormation is correct.

---

## Recommended fix (exact, minimal)

**One file changes: `container/buildspec.yml`.** Rename `imageDetails.json` to
`imageDetail.json` in all three places (the comment, the `printf`, the `cat`,
and the `artifacts.files` list). No CDK code change is needed.

### Diff for `container/buildspec.yml`

```diff
       # imageDetails.json: {ImageURI} shape consumed by the prod CodeDeploy ECS
-      # imageDetails.json: {ImageURI} shape consumed by the prod CodeDeploy ECS
-      # blue/green action to fill the taskdef.json <IMAGE1_NAME> placeholder.
-      - echo "Writing imageDetails.json (prod CodeDeploy blue/green)..."
-      - printf '{"ImageURI":"%s"}' "$REPO_URI:$IMAGE_TAG" > imageDetails.json
+      # imageDetail.json: {ImageURI} shape consumed by the prod CodeDeploy ECS
+      # blue/green action to fill the taskdef.json <IMAGE1_NAME> placeholder.
+      # NOTE: the file name MUST be imageDetail.json (singular) — the
+      # CodeDeployToECS blue/green action hard-requires that exact name.
+      - echo "Writing imageDetail.json (prod CodeDeploy blue/green)..."
+      - printf '{"ImageURI":"%s"}' "$REPO_URI:$IMAGE_TAG" > imageDetail.json
```

```diff
-      - cat imagedefinitions.json imageDetails.json taskdef.json appspec.yaml
+      - cat imagedefinitions.json imageDetail.json taskdef.json appspec.yaml
```

```diff
 artifacts:
   files:
     - imagedefinitions.json
-    - imageDetails.json
+    - imageDetail.json
     - taskdef.json
     - appspec.yaml
```

### Verification after applying

1. `cd infra && npx cdk synth CoffeeShipAppPipeline` still succeeds (no CDK
   change, so this just confirms nothing regressed).
2. Re-run the pipeline (upload `source.zip`). In the Build stage logs, confirm
   `imageDetail.json` is written and that `UPLOAD_ARTIFACTS` lists
   `imageDetail.json`.
3. After approval, the Deploy-Prod `CodeDeployToECS` action should now progress
   past artifact reading and create a CodeDeploy deployment:
   `aws deploy list-deployments --application-name coffee-ship-prod --deployment-group-name coffee-ship-prod --region ap-southeast-1`
   should return a deployment id (previously empty).

### Caveat (not the current failure, but worth checking next)

The brief notes the committed `container/imagedefinitions.json` /
`imageDetails.json` etc. are generated at build time, so there is nothing stale
to rename in the repo beyond the buildspec. If a *committed* `imageDetail.json`
is ever added to `container/` for a build-skip path, it must use the same
singular name.
