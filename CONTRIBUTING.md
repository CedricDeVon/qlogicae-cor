<h1>
    Contribution
</h1>
<p>
    <a href="../README.md">Home</a>
</p>
</br>



<h2 id="introduction">
    👋 Introduction
</h2>
<p>
    Welcome! Any reasonable contribution to this project is greatly appreciated by the team. Having said that, please do your own reading of the project's documentation before making your own contributions.
</p>
</br>



<h2>📚 Table of Contents</h2>
<ul>
    <li>
        <a href="#introduction">
            Introduction
        </a>
    </li>
    <li>
        <a href="#getting-started">
            Getting Started
        </a>
    </li>
    <ul>
        <li>
        <a href="#getting-started-setup">
            Setup
        </a>
        </li>    
    </ul>
    <li>
        <a href="#git">
            Git
        </a>
    </li>
    <ul>
        <li>
            <a href="#git-branch-naming-conventions">
                Branch Naming Conventions
            </a>
        </li>
        <li>
            <a href="#git-verified-commits">
                Verified Commits
            </a>
        </li>    
    </ul>
    <li>
        <a href="#ai">
            AI 
        </a>
    </li>
    <ul>
        <li>
            <a href="#ai-introduction">
                Introduction
            </a>
        </li>
        <li>
            <a href="#ai-allowed">
                Allowed
            </a>
        </li>
        <li>
            <a href="#ai-unallowed">
                Unallowed
            </a>
        </li> 
    </ul>
    <li>
        <a href="#resources">
            Resources
        </a>
    </li>
    <ul>
        <li>
            <a href="#resources-links">
                Links
            </a>
        </li>
    </ul>
</ul>
</br>



<h2 id="getting-started">
    🚀 Getting Started
</h2>
<h3 id="getting-started-setup">
    ⚙️ Setup
</h3>
<p>
    Before you get started with GitHub contributions, please follow the recommended instructions:
</p>
<ol>
    <li>
        <p>
            Fork this repository
        </p>
    </li>
    <li>
        <p>
            Select a filesystem path to clone your forked repository beforehand.
        </p>
    </li>
    <li>
        <p>
            Clone your forked repository at the selected filesystem path.
        </p>
        <pre><code class="language-bash">git clone [repository-url]
cd [repository-directory]</code></pre>
    </li>
    <li>
        <p>
            Create a new branch to push your implementations. Follow the project's git branch naming conventions.
        </p>
        <pre><code class="language-bash">git checkout -b [main-branch-name]/[sub-branch-name]</code></pre>
    </li>
</ol>
</br>



<h2 id="git">
    🔀 Git
</h2>
<h3 id="git-branch-naming-conventions">
    📋 Branch Naming Convention
</h3>
<p>
    Standard branch name examples should look like these: <code>feature/dashboard</code> or <code>bugfix/api</code>. Here is a list of recommended branch names to write and use during development:
</p>
<h4>
    Base Names
</h4>
<p>
    This table shows a collection of recommended base Git branch names as well as what content they should represent.
</p>
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Description</th>  
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>feature</td>
            <td>New planned implementations.</td>
        </tr>
        <tr>
            <td>bugfix</td>
            <td>Attempted issue fixes - even hotfixes.</td>
        </tr>
        <tr>
            <td>test</td>
            <td>Quality-assurance related.</td>
        </tr>
        <tr>
            <td>experiment</td>
            <td>Isolation from development and unstable implementations.</td>
        </tr>
    </tbody>
</table>
<h4>
    Sub Names
</h4>
<p>
    There is no standard naming convention for this part. However, it may be best to take it in the context of the requirement you are aiming to complete. For example, if you are designated to implement a dashboard feature, a reasonable branch name would be <code>feature/dashboard</code>. 
</p>
<p>
    If two or more branch names might cause confusion, you are free to specify, within reason, to specify. For example: <code>feature/dashboard-user</code>. 
</p>
</br>
<h3 id="git-verified-commits">
    ✅ Verified Commits
</h3>
<p>
    Follow each instructions, in-order, and individually supply each macros with the format <code>${{ ... }}</code>:
</p>
<h4>
    Cleaning
</h4>

```cmd
git config --global --unset gpg.format
git config --global --unset user.signingkey
git config --global --unset commit.gpgsign
git config --local --unset gpg.format
git config --local --unset user.signingkey
git config --local --unset commit.gpgsign
```

<h4>
    Setup
</h4>

```cmd
ls ~/.ssh
git config --local --list
ssh-keygen -t ed25519 -C "${{ github-user-email }}" -f ~/.ssh/${{ key }}
cat ~/.ssh/${{ key }}
git config gpg.format ssh
git config user.signingkey ~/.ssh/${{ key }}.pub
git config commit.gpgsign true
```

<p>
    Keep in mind to add your public key as an SSH signing key within your GitHub account.
</p>

</br>



<h2 id="ai">
  🤖 AI
</h2>
<h3 id="ai-introduction">
  👋 Introduction
</h3>
<p>
    This section explains further about AI-related policies.
</p>
<p>
    The team is open to integrating Artificial Intelligence within project implementations and developer workflows. Having said that, there are areas where AI does reasonably well and provides decent results; however, there are other aspects where AI can be a bottleneck. Not precisely in terms of efficiency, but of human artistic expression.
</p>
<h3 id="ai-allowed">
  ✅ Allowed
</h3>
<p>
    Keep in mind ...
</p>
<ol>
    <li>
        <p>
            <strong>DO</strong> use or experiment with any LLMs, AI tools, or AI agents of your choosing. As long as developers can give reasonable results, you have the freedom to work in your own way. Concerning AI-generated output, please consult the <a href="ai-unallowed">AI Unallowed</a> section.
        </p>
    </li>
</ol>
<h3 id="ai-unallowed">
  🚫 Unallowed
</h3>
<p>
    Under any circumstance ...
</p>
<ol>
    <li>
        <p>
            <strong>DO NOT</strong> utilize AI for artistic content (images, icons, videos, etc.). AI-generated content is relatively fast and cheap to create but is frowned upon when used to express one's own work as a human being. If you can reasonably defend yourself for using AI-generated content for a specific use case, please raise your concerns within the GitHub discussions page.
        </p>
    </li>
    <li>
        <p>
            <strong>DO NOT</strong> generate documentation with AI. The entire point of documentation is to defend yourself by giving reasons as to why an implementation has been developed, and why the results are the way they are. It should be written with context to the writer's own perspective - their experience, effort, blood, sweat, and tears.
        </p>
    </li>
    <li>
        <p>
            <strong>DO NOT</strong> use AI-generated code implementations while being unprepared to explain how they work and why they exist. If you do not understand how and why they work, you do not own that implementation. It is also considerate to think about how a team should maintain its reputation and integrity. 
        </p>
    </li>
</ol>
</br> 



<h2 id="resources">
  📖 Resources
</h2>
<h3 id="resources-links">
  🔗 Links
</h3>
<p>
    There are various ways to contribute. You can pick one or two, whichever fits your goals.
</p>
<ul>
  <li>
    <p><a href="./.github/PULL_REQUEST_TEMPLATE.md">Pull Requests</a></p>
  </li>
  <li>
    <p><a href="./.github/ISSUE_TEMPLATE/bug_report.md">Bug Reports</a></p>
  </li>
  <li>
    <p><a href="./.github/ISSUE_TEMPLATE/feature_request.md">Feature Requests</a></p>
  </li>
  <li>
    <p><a href="./CONTRIBUTING.md">Contribution Guidelines</a></p>
  </li>
  <li>
    <p><a href="./SECURITY.md">Security Guidelines</a></p>
  </li>
</ul>
