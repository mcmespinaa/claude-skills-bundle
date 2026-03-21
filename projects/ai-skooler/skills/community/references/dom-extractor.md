# DOM-to-Markdown Extractor

Use this JavaScript function inside `browser_run_code` to extract lesson content from Skool pages.

## Extraction Script

```javascript
// Run inside browser_run_code after navigating to a lesson page
const content = document.querySelector(".tiptap.ProseMirror");
if (!content) throw new Error("No .tiptap.ProseMirror element found");

function processNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    return node.textContent;
  }
  if (node.nodeType !== Node.ELEMENT_NODE) return "";

  const tag = node.tagName.toLowerCase();
  const children = Array.from(node.childNodes).map(processNode).join("");

  switch (tag) {
    case "h1":
      return `# ${children}\n\n`;
    case "h2":
      return `## ${children}\n\n`;
    case "h3":
      return `### ${children}\n\n`;
    case "h4":
      return `#### ${children}\n\n`;
    case "h5":
      return `##### ${children}\n\n`;
    case "h6":
      return `###### ${children}\n\n`;
    case "p":
      return `${children}\n\n`;
    case "strong":
    case "b":
      return `**${children}**`;
    case "em":
    case "i":
      return `*${children}*`;
    case "code":
      if (
        node.parentElement &&
        node.parentElement.tagName.toLowerCase() === "pre"
      ) {
        return children;
      }
      return `\`${children}\``;
    case "pre": {
      const lang =
        node.querySelector("code")?.className?.replace("language-", "") || "";
      return `\`\`\`${lang}\n${children}\n\`\`\`\n\n`;
    }
    case "a": {
      const href = node.getAttribute("href") || "";
      return `[${children}](${href})`;
    }
    case "blockquote":
      return `> ${children.replace(/\n\n/g, "\n> ")}\n\n`;
    case "ul":
      return `${children}\n`;
    case "ol":
      return `${children}\n`;
    case "li": {
      const parent = node.parentElement;
      const isOrdered = parent && parent.tagName.toLowerCase() === "ol";
      const index = isOrdered
        ? Array.from(parent.children).indexOf(node) + 1
        : 0;
      const prefix = isOrdered ? `${index}. ` : "- ";
      return `${prefix}${children.trim()}\n`;
    }
    case "hr":
      return `---\n\n`;
    case "br":
      return "\n";
    case "img":
      return ""; // Skip images — Skool hosts externally
    case "div":
      return children;
    default:
      return children;
  }
}

const markdown = processNode(content).trim();
return markdown;
```

## Usage

```javascript
// In browser_run_code:
const result = await page.evaluate(() => {
  // paste the processNode function above
  const content = document.querySelector(".tiptap.ProseMirror");
  // ... extract and return
});
```

## Notes

- For very long lessons, save output to a temp file instead of returning directly
- The extractor handles nested lists (ul > li > ul) correctly through recursion
- Code blocks: looks for language class on the code element inside pre
- Links: kept as markdown links, not wiki-links — the SKILL.md step converts internal links to wiki-links after extraction
