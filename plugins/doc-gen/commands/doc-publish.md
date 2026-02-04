# /doc-publish — Publish Documentation Site to S3

Upload the generated documentation site to S3 for hosting.

## Instructions

You are running the `/doc-publish` command — the final phase of documentation generation.

### Environment Variables

This command uses two environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SITE_S3_BUCKET` | S3 bucket name for hosting | `my-docs-bucket` |
| `SITE_PROFILE` | AWS CLI profile to use | `default` or `prod` |

If not set, you will be prompted to provide them.

### Prerequisites

1. Check `docs/site/index.html` exists. If not, tell user to run `/doc-site` first and stop.
2. Verify AWS CLI is available: run `aws --version`. If not found, tell user to install AWS CLI and stop.

### Step 1: Check Environment Variables

Run:
```bash
echo "SITE_S3_BUCKET=$SITE_S3_BUCKET"
echo "SITE_PROFILE=$SITE_PROFILE"
```

#### If SITE_S3_BUCKET is not set:
Use AskUserQuestion:
```
S3 bucket not configured. Please provide the S3 bucket name:

Options:
1. Enter bucket name
2. Cancel - I'll set $SITE_S3_BUCKET first
```

If user provides a bucket name, use it. Suggest adding to shell profile:
```bash
export SITE_S3_BUCKET="bucket-name"
```

#### If SITE_PROFILE is not set:
Use AskUserQuestion:
```
AWS profile not configured. Which AWS profile should I use?

Options:
1. default
2. Enter profile name
3. Cancel - I'll set $SITE_PROFILE first
```

If user provides a profile, use it. Suggest adding to shell profile:
```bash
export SITE_PROFILE="profile-name"
```

### Step 2: Verify AWS Credentials

Run: `aws sts get-caller-identity --profile $SITE_PROFILE`
If fails, tell user to configure credentials for the specified profile and stop.

### Step 3: Determine S3 Path

Determine the directory name:
1. Try: `basename $(git rev-parse --show-toplevel 2>/dev/null)` to get the git repo name
2. If not a git repo, use `basename $(pwd)`
3. Sanitize: lowercase, replace spaces with hyphens, remove special characters except hyphens

The full S3 path: `s3://$SITE_S3_BUCKET/{directory-name}/`

### Step 4: Inventory and Confirm

Count files to upload (Glob `docs/site/**/*`). Get total size (`du -sh docs/site/`).

Display and ask for confirmation:
```
Publish Documentation to S3
=============================
Project: {project_name}
Bucket: $SITE_S3_BUCKET
Profile: $SITE_PROFILE
Target: s3://$SITE_S3_BUCKET/{directory-name}/
Files: {count}
Size: {size}

Proceed with upload?
```

Use AskUserQuestion to confirm.

### Step 5: Upload

Run the S3 sync:

```bash
aws s3 sync docs/site/ s3://$SITE_S3_BUCKET/{directory-name}/ --delete --profile $SITE_PROFILE
```

Then fix content types:

```bash
# HTML files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ --recursive --exclude "*" --include "*.html" --content-type "text/html" --metadata-directive REPLACE --profile $SITE_PROFILE --quiet

# CSS files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ --recursive --exclude "*" --include "*.css" --content-type "text/css" --metadata-directive REPLACE --profile $SITE_PROFILE --quiet

# JS files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ --recursive --exclude "*" --include "*.js" --content-type "application/javascript" --metadata-directive REPLACE --profile $SITE_PROFILE --quiet
```

### Step 6: Display Summary

Read `docs/.doc-plan.json` to get the section details. Display the inventory as a box-drawing table:

```
┌─────┬───────────────────┬──────────────────┬──────────────┬─────────────────────────────────┐
│  #  │      Section      │ Files to Analyze │ Output Pages │             Status              │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ 1   │ Architecture (C4) │ {n}              │ {n}          │ Enabled                         │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ ... │ ...               │ ...              │ ...          │ ...                             │
└─────┴───────────────────┴──────────────────┴──────────────┴─────────────────────────────────┘
```

Then display the final URL:

```
Documentation published successfully!

URL: https://$SITE_S3_BUCKET.s3.amazonaws.com/{directory-name}/index.html
```

### Error Handling

- If AWS CLI not installed: provide install link
- If credentials fail: suggest `aws configure --profile $SITE_PROFILE`
- If upload fails (AccessDenied): check bucket policy and IAM s3:PutObject permission
- If upload fails (NoSuchBucket): verify bucket name
- If environment variables missing: prompt user via AskUserQuestion
