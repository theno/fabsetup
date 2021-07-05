<script>
// https://stackoverflow.com/a/9541579
function isOverflownWidth(element) {
  return element.scrollWidth > element.clientWidth;
}
function isOverflownHeigth(element) {
  return element.scrollHeight > element.clientHeight;
}
function isOverflown(element) {
  return isOverflownWidth(element) || isOverflownHeight(element);
}
function setPaddingBottom(element) {
  if (isOverflownWidth(element)) {
    element.style.paddingBottom = '18px';
  }
  else {
    element.style.paddingBottom = '5px';
  }
}

var items = document.getElementsByClassName('sh');
for (var i=0, len=items.length|0; i<len; i=i+1|0) {

  setPaddingBottom(items[i]);
  items[i].style.height = 'auto';

  items[i].onclick = function() {
    if (this.style.height === 'auto') {
      this.style.height = '24px';
    }
    else {
      this.style.height = 'auto';
    }
    setPaddingBottom(this);
  }
};
</script>

