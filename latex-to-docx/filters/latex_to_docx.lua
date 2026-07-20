-- Conservative Pandoc filter for LaTeX -> DOCX.
-- It marks unhandled raw TeX visibly in non-strict diagnostic runs instead of
-- allowing a writer to discard it without evidence. The Python orchestrator
-- sets LATEX_TO_DOCX_STRICT=1 for strict runs and inspects the JSON AST first.

local strict = os.getenv('LATEX_TO_DOCX_STRICT') == '1'

local function raw_marker(kind, text)
  local payload = string.format('[UNRESOLVED %s: %s]', kind, text)
  if strict then
    error(payload)
  end
  return pandoc.Span({pandoc.Str(payload)}, {class='latex-unresolved'})
end

function RawInline(el)
  if el.format == 'tex' or el.format == 'latex' then
    return raw_marker('RAW INLINE', el.text)
  end
end

function RawBlock(el)
  if el.format == 'tex' or el.format == 'latex' then
    if strict then
      error('[UNRESOLVED RAW BLOCK: ' .. el.text .. ']')
    end
    return pandoc.Para({raw_marker('RAW BLOCK', el.text)})
  end
end

-- Preserve source labels as attributes where Pandoc already represents them.
function Header(el)
  if el.identifier == '' then
    return el
  end
  el.attributes['latex-label'] = el.identifier
  return el
end
