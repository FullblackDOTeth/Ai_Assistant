# Pipeline Monitor Setup Guide

## Step 1: Generate GitHub Personal Access Token (PAT)

1. Go to GitHub.com and log in
2. Click your profile picture (top right)
3. Go to Settings
4. Scroll down to "Developer settings" (bottom of left sidebar)
5. Click "Personal access tokens" → "Tokens (classic)"
6. Click "Generate new token" → "Generate new token (classic)"
7. Configure the token:
   - Name: "Pipeline Monitor Token"
   - Expiration: Choose based on your needs (e.g., 90 days)
   - Permissions:
     - ✓ `repo` (full control)
     - ✓ `workflow` (workflow control)
8. Click "Generate token"
9. **IMPORTANT**: Copy the token immediately - you won't see it again!

## Step 2: Run Setup Script

1. Open a command prompt
2. Navigate to your project directory
3. Run the setup script:
   ```bash
   python testing/utils/setup_environment.py
   ```
4. Enter the requested information:
   - GitHub Personal Access Token (from Step 1)
   - Your GitHub username
   - Your repository name

## Step 3: Set Environment Variables

1. Navigate to `testing/scripts` folder
2. Run `set_environment.bat`
3. Wait for confirmation that variables are set
4. Close and reopen any command prompts

## Step 4: Verify Setup

1. Open a new command prompt
2. Run:
   ```bash
   echo %GITHUB_TOKEN%
   echo %GITHUB_OWNER%
   echo %GITHUB_REPO%
   ```
3. Verify that each variable shows the correct value

## Step 5: Run Pipeline Monitor

1. Run the monitor:
   ```bash
   python testing/utils/pipeline_monitor.py
   ```
2. You should see the monitoring dashboard with:
   - Overview tab
   - Test Results tab
   - Coverage tab

## Troubleshooting

If you encounter issues:

1. **Variables not set**:
   - Run `set_environment.bat` again
   - Make sure to open a new command prompt

2. **Authentication errors**:
   - Verify your PAT hasn't expired
   - Check that the token has correct permissions

3. **Monitor shows no data**:
   - Verify repository name and owner
   - Ensure you have active workflow runs

## Security Note

- Keep your PAT secure
- Don't share your configuration files
- Don't commit them to version control
