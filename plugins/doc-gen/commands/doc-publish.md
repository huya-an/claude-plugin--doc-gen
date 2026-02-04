# /doc-publish — Publish Documentation Site to S3

Upload the generated documentation site to S3 for hosting.

## Instructions

You are running the `/doc-publish` command — the final phase of documentation generation.

### Prerequisites

1. Check `docs/site/index.html` exists. If not, tell user to run `/doc-site` first and stop.
2. Verify AWS CLI is available: run `aws --version`. If not found, tell user to install AWS CLI and stop.
3. Verify AWS credentials: run `aws sts get-caller-identity`. If fails, tell user to configure credentials and stop.

### Step 1: Determine S3 Path

The target bucket is: `repo-documentation-918308113460`

Determine the directory name:
1. Try: `basename $(git rev-parse --show-toplevel 2>/dev/null)` to get the git repo name
2. If not a git repo, use `basename $(pwd)`
3. Sanitize: lowercase, replace spaces with hyphens, remove special characters except hyphens

The full S3 path: `s3://repo-documentation-918308113460/{directory-name}/`

### Step 2: Inventory and Confirm

Count files to upload (Glob `docs/site/**/*`). Get total size (`du -sh docs/site/`).

Display and ask for confirmation:
```
Publish Documentation to S3
=============================
Project: {project_name}
Target: s3://repo-documentation-918308113460/{directory-name}/
Files: {count}
Size: {size}

Proceed with upload?
```

Use AskUserQuestion to confirm.

### Step 3: Upload

Run the S3 sync:

```bash
aws s3 sync docs/site/ s3://repo-documentation-918308113460/{directory-name}/ --delete
```

Then fix content types:

```bash
# HTML files
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ s3://repo-documentation-918308113460/{directory-name}/ --recursive --exclude "*" --include "*.html" --content-type "text/html" --metadata-directive REPLACE --quiet

# CSS files
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ s3://repo-documentation-918308113460/{directory-name}/ --recursive --exclude "*" --include "*.css" --content-type "text/css" --metadata-directive REPLACE --quiet

# JS files
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ s3://repo-documentation-918308113460/{directory-name}/ --recursive --exclude "*" --include "*.js" --content-type "application/javascript" --metadata-directive REPLACE --quiet

# XML/drawio files
aws s3 cp s3://repo-documentation-918308113460/{directory-name}/ s3://repo-documentation-918308113460/{directory-name}/ --recursive --exclude "*" --include "*.drawio" --content-type "application/xml" --metadata-directive REPLACE --quiet
```

### Step 4: Display Summary

Read `docs/.doc-plan.json` to get the section details. For each section, count the files in `docs/.doc-manifest.json` and the output files.

Display the inventory as a box-drawing table:

```
┌─────┬───────────────────┬──────────────────┬──────────────┬─────────────────────────────────┐
│  #  │      Section      │ Files to Analyze │ Output Pages │             Status              │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ 1   │ Architecture (C4) │ {n}              │ {n}          │ Enabled                         │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ 2   │ API Plane         │ {n}              │ {n}          │ Enabled                         │
├─────┼───────────────────┼──────────────────┼──────────────┼─────────────────────────────────┤
│ ... │ ...               │ ...              │ ...          │ ...                             │
└─────┴───────────────────┴──────────────────┴──────────────┴─────────────────────────────────┘
```

For each section in the plan:
- If `enabled: true` and has files: show file count and output page count, status "Enabled"
- If `enabled: true` but 0 files: status "Enabled (no files found)"
- If `enabled: false` or missing: status "Skipped ({reason})"

Count output pages from the `output_files` array in the plan, or by counting actual `docs/md/*.md` files that match the section prefix.

Then display the final URL:

```
Documentation published successfully!

URL: https://repo-documentation-918308113460.s3.amazonaws.com/{directory-name}/index.html
```

### Error Handling

- If AWS CLI not installed: provide install link
- If credentials fail: suggest `aws configure` or check IAM permissions
- If upload fails (AccessDenied): check bucket policy and IAM s3:PutObject permission
- If upload fails (NoSuchBucket): verify bucket name
- If partial upload failure: report which files failed and suggest re-running
