-- Force all figures to [H] placement (no floating) — works with Pandoc 3.x

-- Handle Figure elements (Pandoc 2.11+ / 3.x)
-- AST: Figure(attr)(Caption)([ Plain [Image ...] ])
function Figure(el)
  local caption = pandoc.utils.stringify(el.caption)
  local body = el.content[1]   -- first Block = Plain [Image ...]
  local img = nil
  if body and body.content then
    for _, inline in ipairs(body.content) do  -- inlines inside Plain
      if inline.t == "Image" then
        img = inline
        break
      end
    end
  end
  if img then
    local src = img.src
    local latex = '\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth,keepaspectratio]{' .. src .. '}\n'
    if caption ~= "" then
      latex = latex .. '\\caption*{' .. caption .. '}\n'
    end
    latex = latex .. '\\end{figure}'
    return pandoc.RawBlock('latex', latex)
  end
end

-- Fallback for older Pandoc: standalone image in a Para
function Para(el)
  if #el.content == 1 and el.content[1].t == "Image" then
    local img = el.content[1]
    local caption = pandoc.utils.stringify(img.caption)
    local src = img.src
    local latex = '\\begin{figure}[H]\n\\centering\n\\includegraphics[width=\\linewidth,keepaspectratio]{' .. src .. '}\n'
    if caption ~= "" then
      latex = latex .. '\\caption*{' .. caption .. '}\n'
    end
    latex = latex .. '\\end{figure}'
    return pandoc.RawBlock('latex', latex)
  end
end
