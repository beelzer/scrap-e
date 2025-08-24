/**
 * Renovate Configuration for Advanced Scenarios
 * This file provides additional configuration for Renovate that can't be expressed in JSON
 */

module.exports = {
  /**
   * Custom manager for Python dependencies using uv
   */
  customManagers: [
    {
      customType: 'regex',
      fileMatch: ['pyproject\\.toml'],
      matchStrings: [
        // Match dependencies in [project.dependencies]
        '\\[project\\.dependencies\\][\\s\\S]*?"(?<depName>[^"]+)(?<currentValue>[^"]*)"',
        // Match dev dependencies
        '\\[project\\.optional-dependencies\\.dev\\][\\s\\S]*?"(?<depName>[^"]+)(?<currentValue>[^"]*)"',
      ],
      datasourceTemplate: 'pypi',
      versioningTemplate: 'pep440',
    },
  ],

  /**
   * Custom commit message templates
   */
  commitMessageExtra: '{{#if isMajor}}🚨 BREAKING CHANGE{{/if}}',
  commitMessageSuffix: '',

  /**
   * PR body template
   */
  prBodyTemplate: `
## 📦 Dependency Update

{{#if isPin}}📌 **Pinning** {{depName}} to {{newVersion}}{{/if}}
{{#if isRollback}}⏪ **Rolling back** {{depName}} from {{currentVersion}} to {{newVersion}}{{/if}}
{{#if isReplacement}}🔄 **Replacing** {{depName}} with {{newName}}{{/if}}
{{#if isPatch}}🩹 **Patch update**{{/if}}
{{#if isMinor}}✨ **Minor update**{{/if}}
{{#if isMajor}}💥 **Major update** - Breaking changes possible{{/if}}

### Changes
- **Package**: \`{{depName}}\`
- **Type**: {{depType}}
- **Current**: {{currentVersion}}
- **New**: {{newVersion}}
{{#if releases}}
- **Release Notes**: [View Changelog]({{releases.[0].releaseNotes.url}})
{{/if}}

### Testing Checklist
- [ ] All CI checks pass
- [ ] No security vulnerabilities introduced
- [ ] Application builds successfully
- [ ] Unit tests pass
- [ ] Integration tests pass
{{#if isMajor}}
- [ ] Manual testing completed for breaking changes
- [ ] Documentation updated if needed
{{/if}}

### Auto-Merge Status
{{#if automerge}}
✅ **This PR will be auto-merged once all checks pass**
{{else}}
🔍 **This PR requires manual review**
{{/if}}

---
<details>
<summary>📊 Dependency Details</summary>

\`\`\`json
{
  "package": "{{depName}}",
  "currentVersion": "{{currentVersion}}",
  "newVersion": "{{newVersion}}",
  "updateType": "{{updateType}}",
  "datasource": "{{datasource}}"
}
\`\`\`

</details>

---
🤖 _This PR was automatically created by Renovate Bot_
`,

  /**
   * Regex managers for additional file types
   */
  regexManagers: [
    {
      fileMatch: ['\\.github/workflows/.*\\.ya?ml$'],
      matchStrings: [
        'uses: (?<depName>[^/]+/[^/@]+)(?:/[^@]+)?@(?<currentValue>[^\\s]+)',
      ],
      datasourceTemplate: 'github-tags',
    },
  ],

  /**
   * Group presets for better organization
   */
  groupPresets: {
    pythonCore: {
      description: 'Core Python packages',
      matchPackagePatterns: ['^python$', '^pip$', '^setuptools$', '^wheel$'],
    },
    pythonTesting: {
      description: 'Python testing packages',
      matchPackagePatterns: ['^pytest', '^coverage', '^tox', '^hypothesis'],
    },
    pythonLinting: {
      description: 'Python linting packages',
      matchPackagePatterns: ['^ruff', '^black', '^isort', '^mypy', '^pylint'],
    },
  },
};
