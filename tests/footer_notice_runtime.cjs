'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/footer_notice_fix.js'), 'utf8');
const text = value => ({nodeType: 3, nodeValue: value});
const element = children => ({
  nodeType: 1,
  children,
  get textContent() { return this.children.map(n => n.nodeType === 3 ? n.nodeValue : n.textContent).join(''); }
});
const allTexts = node => node.nodeType === 3 ? [node] : node.children.flatMap(allTexts);
const notice = text('Основа — перевод Б. Баймуханбетова (2006). Учебные задания требуют проверки.');
const unaffected = text('Текст книги: исходное содержание неизменно.');
const root = element([element([notice]), element([unaffected])]);
let observer;
class Observer {
  constructor(callback) { this.callback = callback; observer = this; }
  observe(node, options) {
    assert.equal(node, root);
    assert.equal(options.childList, true);
    assert.equal(options.subtree, true);
    assert.equal(options.characterData, true);
  }
}
const document = {
  getElementById: id => id === 'root' ? root : null,
  createTreeWalker: node => {
    const nodes = allTexts(node);
    let index = 0;
    return {nextNode: () => nodes[index++] ?? null};
  }
};
vm.runInNewContext(script, {
  document, window: {}, MutationObserver: Observer,
  Node: {TEXT_NODE: 3, ELEMENT_NODE: 1}, NodeFilter: {SHOW_TEXT: 4}
});
assert.equal(notice.nodeValue, 'Основа — перевод Б. Баймуханбетова (2006).');
assert.equal(unaffected.nodeValue, 'Текст книги: исходное содержание неизменно.');
const rerendered = element([text('Перевод сохранён. Учебные задания требуют проверки.')]);
observer.callback([{type: 'childList', addedNodes: [rerendered]}]);
assert.equal(rerendered.textContent, 'Перевод сохранён.');
const textUpdate = text('Учебные задания требуют проверки.');
observer.callback([{type: 'characterData', target: textUpdate}]);
assert.equal(textUpdate.nodeValue, '');
console.log('Footer notice: initial render, rerender, text update and unaffected content OK');
