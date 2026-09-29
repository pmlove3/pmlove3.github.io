local SITE_URL = "https://paulmaxlove.com/"
local PERSON_ID = SITE_URL .. "#person"

local function text(value)
  if value == nil then
    return ""
  end
  return pandoc.utils.stringify(value)
end

local function json_string(value)
  local escaped = text(value)
    :gsub("\\", "\\\\")
    :gsub('"', '\\"')
    :gsub("\b", "\\b")
    :gsub("\f", "\\f")
    :gsub("\n", "\\n")
    :gsub("\r", "\\r")
    :gsub("\t", "\\t")
  return '"' .. escaped .. '"'
end

local function canonical_url()
  local input_file = quarto.doc.input_file or ""
  local relative_path = pandoc.path.make_relative(input_file, quarto.project.directory)
    :gsub("\\", "/")
    :gsub("^%./", "")
    :gsub("%.qmd$", ".html")
  return SITE_URL .. relative_path
end

local function person_json()
  return table.concat({
    '{"@type":"Person"',
    ',"@id":' .. json_string(PERSON_ID),
    ',"name":"Paul Max Love III"',
    ',"url":' .. json_string(SITE_URL),
    '}',
  })
end

local function blog_posting_json(meta)
  return table.concat({
    '{"@context":"https://schema.org"',
    ',"@type":"BlogPosting"',
    ',"headline":' .. json_string(meta.title),
    ',"datePublished":' .. json_string(meta["schema-date"]),
    ',"description":' .. json_string(meta.description),
    ',"url":' .. json_string(canonical_url()),
    ',"author":' .. person_json(),
    '}',
  })
end

local function course_json(meta)
  local provider = table.concat({
    '{"@type":"CollegeOrUniversity"',
    ',"name":"New York University Abu Dhabi"',
    ',"url":"https://nyuad.nyu.edu/"',
    '}',
  })

  return table.concat({
    '{"@context":"https://schema.org"',
    ',"@type":"Course"',
    ',"name":' .. json_string(meta["course-name"]),
    ',"description":' .. json_string(meta.description),
    ',"url":' .. json_string(canonical_url()),
    ',"provider":' .. provider,
    ',"hasCourseInstance":{"@type":"CourseInstance","instructor":' .. person_json() .. '}',
    '}',
  })
end

local function course_list_json(meta)
  local items = {}

  for position, path in ipairs(meta["course-list"] or {}) do
    table.insert(items, table.concat({
      '{"@type":"ListItem"',
      ',"position":' .. tostring(position),
      ',"url":' .. json_string(SITE_URL .. text(path)),
      '}',
    }))
  end

  return table.concat({
    '{"@context":"https://schema.org"',
    ',"@type":"ItemList"',
    ',"itemListElement":[' .. table.concat(items, ",") .. ']',
    '}',
  })
end

function Meta(meta)
  local schema_type = text(meta["schema-type"])
  local json = nil

  if schema_type == "blog-posting" then
    json = blog_posting_json(meta)
  elseif schema_type == "course" then
    json = course_json(meta)
  elseif schema_type == "course-list" then
    json = course_list_json(meta)
  end

  if json ~= nil then
    quarto.doc.include_text(
      "in-header",
      '<script type="application/ld+json">\n' .. json .. '\n</script>'
    )
  end

  return meta
end
