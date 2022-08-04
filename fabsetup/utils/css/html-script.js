<footer id="page_footer">
<a id="collapse_expand" href="" title="collapse / expand command output">collapse / expand</a>
</footer>

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
}

var cur_height = 'auto';
var a = document.getElementById("collapse_expand");

a.onclick = function() {

  if (cur_height === 'auto') {
    cur_height = '24px';
  }
  else {
    cur_height = 'auto';
  }

  for (var i=0, len=items.length|0; i<len; i=i+1|0) {
    items[i].style.height = cur_height;
    setPaddingBottom(items[i]);
  }

  return false;
}

</script>
