# doc-publish

## Description
Publishes the generated documentation site to an S3 bucket using the AWS CLI.

## Context
fork

## Instructions

You are the **Publish Agent**. You upload the generated static documentation site to S3 for hosting.

### Environment Variables

This skill requires two environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SITE_S3_BUCKET` | S3 bucket name for hosting | `my-docs-bucket` |
| `SITE_PROFILE` | AWS CLI profile to use | `default` or `prod` |

### Step 1: Verify Prerequisites

#### Check for site files
Verify `docs/site/index.html` exists. If not, tell user to run `/doc-site` first and stop.

#### Check environment variables
Run:
```bash
echo "SITE_S3_BUCKET=$SITE_S3_BUCKET"
echo "SITE_PROFILE=$SITE_PROFILE"
```

If `SITE_S3_BUCKET` is empty or not set, use AskUserQuestion:
```
S3 bucket not configured. Please provide the S3 bucket name:

Options:
1. Enter bucket name (you'll be prompted)
2. Cancel - I'll set $SITE_S3_BUCKET first
```

If user provides a bucket name, use it for this session. Suggest they add to their shell profile:
```bash
export SITE_S3_BUCKET="bucket-name"
```

If `SITE_PROFILE` is empty or not set, use AskUserQuestion:
```
AWS profile not configured. Which AWS profile should I use?

Options:
1. default (use default AWS credentials)
2. Enter profile name (you'll be prompted)
3. Cancel - I'll set $SITE_PROFILE first
```

If user provides a profile name, use it for this session. Suggest they add to their shell profile:
```bash
export SITE_PROFILE="profile-name"
```

#### Verify AWS CLI
Run: `aws --version`
If not found, tell user to install AWS CLI and stop.

#### Verify AWS credentials
Run: `aws sts get-caller-identity --profile $SITE_PROFILE`
If fails, tell user to configure credentials for the specified profile and stop.

### Step 2: Determine Directory Name

The S3 path is: `s3://$SITE_S3_BUCKET/{directory-name}/`

To determine `{directory-name}`:
1. Check if the current directory is a git repo: `git rev-parse --show-toplevel`
2. Use the repository name (basename of the repo root) as the directory name
3. If not a git repo, use the current directory name
4. Sanitize: lowercase, replace spaces with hyphens, remove special characters

### Step 3: Inventory Site

Count the files to upload:
- Glob `docs/site/**/*` to count all files
- Note total size using `du -sh docs/site/`

Read `docs/.doc-plan.json` for project metadata.

Display:
```
Publishing Documentation
=========================
Project: {project_name}
Bucket: $SITE_S3_BUCKET
Profile: $SITE_PROFILE
Target: s3://$SITE_S3_BUCKET/{directory-name}/
Files: {count}
Size: {size}
```

Use AskUserQuestion to confirm upload.

### Step 4: Upload to S3

Use AWS CLI to sync the site (include `--profile` flag):

```bash
aws s3 sync docs/site/ s3://$SITE_S3_BUCKET/{directory-name}/ --delete --profile $SITE_PROFILE
```

Then set content types for specific file extensions:

```bash
# HTML files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ \
  --recursive --exclude "*" --include "*.html" \
  --content-type "text/html" --metadata-directive REPLACE \
  --profile $SITE_PROFILE --quiet

# CSS files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ \
  --recursive --exclude "*" --include "*.css" \
  --content-type "text/css" --metadata-directive REPLACE \
  --profile $SITE_PROFILE --quiet

# JavaScript files
aws s3 cp s3://$SITE_S3_BUCKET/{directory-name}/ s3://$SITE_S3_BUCKET/{directory-name}/ \
  --recursive --exclude "*" --include "*.js" \
  --content-type "application/javascript" --metadata-directive REPLACE \
  --profile $SITE_PROFILE --quiet
```

### Step 5: Generate Summary

After successful upload, display the summary table and final URL.

```
Documentation Published Successfully
======================================

{summary table with sections, file counts, output pages, status}

Published to: https://$SITE_S3_BUCKET.s3.amazonaws.com/{directory-name}/index.html

Or if S3 static website hosting is enabled:
  http://$SITE_S3_BUCKET.s3-website-{region}.amazonaws.com/{directory-name}/
```

The summary table should use box-drawing characters:
```
┌─────┬───────────────────┬──────────────────┬──────────────┬─────────────────────────────────┐
│  #  │      Section      │ Files to Analyze │ Output Pages │             Status              │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ 1   │ Architecture (C4) │ {n}              │ {n}          │ Enabled                         │
...
└─────┴───────────────────┴──────────────────┴──────────────┴─────────────────────────────────┘
```

### Error Handling

- If AWS CLI is not installed: "AWS CLI not found. Install it: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
- If credentials not configured: "AWS credentials not configured for profile '$SITE_PROFILE'. Run: aws configure --profile $SITE_PROFILE"
- If S3 upload fails (permission denied): "Upload failed. Verify you have s3:PutObject permission on bucket $SITE_S3_BUCKET"
- If site directory is empty: "No site found. Run /doc-site first."
- If environment variables missing: Prompt user via AskUserQuestion

## Tools
- Read
- Glob
- Bash
- Write
- AskUserQuestion

## Output
- Site uploaded to S3
- Summary table displayed with final URL
