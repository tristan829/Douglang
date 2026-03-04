hljs.registerLanguage('douglang', function(hljs) {
  return {
    name: 'Douglang',
    contains: [
      { className: 'keyword', begin: /\+set|-set|\*set|\/set|%set|set|tts|prediction|Believers|Doubters|win|loop|break/ },
      { className: 'keyword', begin: /(Doug)+/ },
      { className: 'keyword', begin: /Bald/ },
      { className: 'number', begin: /(\d+(\.\d+)?|\.\d+)/, relevance: 0 },
      hljs.QUOTE_STRING_MODE,
      hljs.C_LINE_COMMENT_MODE,
      hljs.C_BLOCK_COMMENT_MODE,
    ]
  };
});

// Highlight inline code blocks
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('code.language-douglang').forEach((el) => hljs.highlightElement(el));
});