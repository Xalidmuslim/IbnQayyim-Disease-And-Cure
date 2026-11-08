/* v50: Remove the obsolete homepage claim without altering the book or the editorial credits. */
(() => {
  'use strict';
  const obsolete = 'Учебные задания требуют проверки.';
  const root = document.getElementById('root');
  if (!root || window.__footerNoticeFixV50) return;
  window.__footerNoticeFixV50 = true;

  const correct = node => {
    if (node.nodeType === Node.TEXT_NODE) {
      if (node.nodeValue && node.nodeValue.includes(obsolete)) {
        node.nodeValue = node.nodeValue.replace(obsolete, '').replace(/[ \t]+$/, '');
      }
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE || !node.textContent.includes(obsolete)) return;
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    let textNode;
    while ((textNode = walker.nextNode())) correct(textNode);
  };

  correct(root);
  new MutationObserver(records => {
    for (const record of records) {
      if (record.type === 'characterData') correct(record.target);
      else if (record.type === 'childList') {
        for (const added of record.addedNodes) correct(added);
      }
    }
  }).observe(root, {childList: true, subtree: true, characterData: true});
})();
