<?xml version="1.0" encoding="UTF-8"?>
<formats${' id="'+ h.urlescape(identifier) + '"' if identifier else ''|n}>
% for format in formats:
<format name="${format.unapi_name}" type="${format.mimetype}" />
% endfor
</formats>
