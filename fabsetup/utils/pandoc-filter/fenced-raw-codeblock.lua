-- taken from tarleb's answer: https://stackoverflow.com/a/66982937

local fenced = '```\n%s\n```\n'
function CodeBlock (cb)
  return pandoc.RawBlock('markdown', fenced:format(cb.text))
end
