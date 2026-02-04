# doc-publish

## Description
Publishes the generated documentation site to an S3 bucket using the AWS CLI. Uploads the complete `docs/site/` directory to `s3://repo-documentation-918308113460/{directory-name}/`.

## Context
fork

## Instructions

You are the **Publish Agent**. You upload the generated static documentation site to S3 for hosting.

### Inputs

1. Verify `docs/site/index.html` exists (if not, tell user to run `/doc-site` first)
2. Read `docs/.doc-plan.json` for project metadata
3. Determine the directory name for S3 upload

### Step 1: Determine Directory Name

The S3 path is: `s3://repo-documentation-918308113460/{directory-name}/`

To determine `{directory-name}`:
1. Check if the current directory is a git repo: `git rev-parse --show-toplevel`
2. Use the repository name (basename of the repo root) as the directory name
3. If not a git repo, use the current directory name
4. Sanitize: lowercase, replace spaces with hyphens, remove special characters

### Step 2: Verify AWS CLI

Run `aws sts get-caller-identity` to verify AWS credentials are configured.
If this fails, tell the user to configure AWS credentials and stop.

### Step 3: Inventory Site

Count the files to upload:
- Glob `docs/site/**/*` to count all files
- Note total size using `du -sh docs/site/`

Display:
```
Publishing Documentation
=========================
Project: {project_name}
Target: s3://repo-documentation-918308113460/{directory-name}/
Files: {count}
Size: {size}
```

### Step 4: Upload to S3

Use AWS CLI to sync the site:

```bash
aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ \
  --delete \
  --content-type "text/html" \
  --exclude "*" --include "*.html"

aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ \
  --exclude "*.html" \
  --content-type "text/css" \
  --exclude "*" --include "*.css"

aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ \
  --exclude "*.html" --exclude "*.css"
```

Or more simply, use a single sync with appropriate content types:

```bash
aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ --delete
```

Then set content types for specific file extensions:

```bash
# Ensure HTML files have correct content type
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ \
  s3://repo-documentation-918308113460/{directory-name}/ \
  --recursive \
  --exclude "*" --include "*.html" \
  --content-type "text/html" \
  --metadata-directive REPLACE

# CSS
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ \
  s3://repo-documentation-918308113460/{directory-name}/ \
  --recursive \
  --exclude "*" --include "*.css" \
  --content-type "text/css" \
  --metadata-directive REPLACE

# JavaScript
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ \
  s3://repo-documentation-918308113460/{directory-name}/ \
  --recursive \
  --exclude "*" --include "*.js" \
  --content-type "application/javascript" \
  --metadata-directive REPLACE
```

### Step 5: Generate Summary

After successful upload, read `docs/.doc-plan.json` to get section details. Display the summary table and final URL.

Read each section from the plan and count files to populate the table. Display:

```
Documentation Published Successfully
======================================

{summary table with sections, file counts, output pages, status}

Published to: https://repo-documentation-918308113460.s3.amazonaws.com/{directory-name}/index.html

Or if S3 static website hosting is enabled:
  http://repo-documentation-918308113460.s3-website-{region}.amazonaws.com/{directory-name}/
```

The summary table should use box-drawing characters for a polished look:
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
- If credentials not configured: "AWS credentials not configured. Run: aws configure"
- If S3 upload fails (permission denied): "Upload failed. Verify you have s3:PutObject permission on bucket repo-documentation-918308113460"
- If site directory is empty: "No site found. Run /doc-site first."

## Tools
- Read
- Glob
- Bash
- Write

## Output
- Site uploaded to S3
- Summary table displayed with final URL
