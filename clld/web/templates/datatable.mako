<table id="${datatable.eid}" cellpadding="0" cellspacing="0" border="0" class="table table-condensed table-bordered table-striped">
    <thead>
        <tr>
            % for col in datatable.cols:
            <th>${col.js_args['sTitle']}</th>
            % endfor
        </tr>
    </thead>
    <tbody>
        % if not datatable.server_side:
            % for item in datatable.get_query():
            <tr>
                % for col in datatable.cols:
                <td>${col.format(item)}</td>
                % endfor
            </tr>
            % endfor
        % endif
    </tbody>
    % if datatable.search == 'col':
    <tfoot>
	<tr>
            % for col in datatable.cols:
	    <th style="text-align: left;">
                % if col.js_args['bSearchable']:
		    % if hasattr(col, 'choices'):
		    <select class="control" name="${col.name}">
			<option value="">--any--</option>
			% for val in getattr(col, 'choices'):
			<option value="${val}">${val}</option>
			% endfor
		    </select>
		    % else:
		    <input type="text" name="${col.name}" value="" placeholder="Search ${col.js_args['sTitle']}" class="input-small control" />
		    % endif
                % else:
                    <input type="text" name="${col.name}" value="" class="search_init control" style="display: none;"/>
                % endif
            </th>
            % endfor
	</tr>

    </tfoot>
    % endif
</table>
<script>
$(document).ready( function() {
    /*
     * TODO: replace with
     * CLLD.DataTable.init("${datatable.eid}", h.dumps(datatable.options))
     */

    $.extend($.fn.dataTable.defaults, {
        "bServerSide": true,
        "bStateSave": true,
        //"sDom": '<"H"l<"dt-toolbar">fr>t<"F"ip>',
	"sDom": "<'row-fluid'<'span6'l><'span6'f<'dt-toolbar'>>r>t<'row-fluid'<'span6'i><'span6'p>>",
        "fnServerParams": function (aoData) {
	        % if datatable.search == 'global_col':
            aoData.push({"name": "searchCol", "value": $('#searchCol').val()});
	        % endif
			aoData.push({"name": "__eid__", "value": "${datatable.eid}"});
        },
        % if datatable.search == 'col':
        "fnInitComplete": function(oSettings) {
            for ( var i=0 ; i<oSettings.aoPreSearchCols.length ; i++ ){
                if(oSettings.aoPreSearchCols[i].sSearch.length>0){
					var ctrl = $("tfoot .control")[i];
					ctrl = $(ctrl);
					if (ctrl.length) {
						ctrl.val(oSettings.aoPreSearchCols[i].sSearch);
					} else {
						alert(ctrl);
					}
                    //$("tfoot input")[i].className = "";
                }
            }
        },
        % endif
        "bJQueryUI": false,
	"bAutoWidth": false,
	"sPaginationType": "bootstrap"
    });


$.extend( $.fn.dataTableExt.oStdClasses, {
    "sWrapper": "dataTables_wrapper form-inline"
} );




/* API method to get paging information */
$.fn.dataTableExt.oApi.fnPagingInfo = function ( oSettings )
{
	return {
		"iStart":         oSettings._iDisplayStart,
		"iEnd":           oSettings.fnDisplayEnd(),
		"iLength":        oSettings._iDisplayLength,
		"iTotal":         oSettings.fnRecordsTotal(),
		"iFilteredTotal": oSettings.fnRecordsDisplay(),
		"iPage":          Math.ceil( oSettings._iDisplayStart / oSettings._iDisplayLength ),
		"iTotalPages":    Math.ceil( oSettings.fnRecordsDisplay() / oSettings._iDisplayLength )
	};
};


/* Bootstrap style pagination control */
$.extend( $.fn.dataTableExt.oPagination, {
	"bootstrap": {
		"fnInit": function( oSettings, nPaging, fnDraw ) {
			var oLang = oSettings.oLanguage.oPaginate;
			var fnClickHandler = function ( e ) {
				e.preventDefault();
				if ( oSettings.oApi._fnPageChange(oSettings, e.data.action) ) {
					fnDraw( oSettings );
				}
			};

			$(nPaging).addClass('pagination').append(
				'<ul>'+
					'<li class="prev disabled"><a href="#">&larr; '+oLang.sPrevious+'</a></li>'+
					'<li class="next disabled"><a href="#">'+oLang.sNext+' &rarr; </a></li>'+
				'</ul>'
			);
			var els = $('a', nPaging);
			$(els[0]).bind( 'click.DT', { action: "previous" }, fnClickHandler );
			$(els[1]).bind( 'click.DT', { action: "next" }, fnClickHandler );
		},

		"fnUpdate": function ( oSettings, fnDraw ) {
			var iListLength = 5;
			var oPaging = oSettings.oInstance.fnPagingInfo();
			var an = oSettings.aanFeatures.p;
			var i, j, sClass, iStart, iEnd, iHalf=Math.floor(iListLength/2);

			if ( oPaging.iTotalPages < iListLength) {
				iStart = 1;
				iEnd = oPaging.iTotalPages;
			}
			else if ( oPaging.iPage <= iHalf ) {
				iStart = 1;
				iEnd = iListLength;
			} else if ( oPaging.iPage >= (oPaging.iTotalPages-iHalf) ) {
				iStart = oPaging.iTotalPages - iListLength + 1;
				iEnd = oPaging.iTotalPages;
			} else {
				iStart = oPaging.iPage - iHalf + 1;
				iEnd = iStart + iListLength - 1;
			}

			for ( i=0, iLen=an.length ; i<iLen ; i++ ) {
				// Remove the middle elements
				$('li:gt(0)', an[i]).filter(':not(:last)').remove();

				// Add the new list items and their event handlers
				for ( j=iStart ; j<=iEnd ; j++ ) {
					sClass = (j==oPaging.iPage+1) ? 'class="active"' : '';
					$('<li '+sClass+'><a href="#">'+j+'</a></li>')
						.insertBefore( $('li:last', an[i])[0] )
						.bind('click', function (e) {
							e.preventDefault();
							oSettings._iDisplayStart = (parseInt($('a', this).text(),10)-1) * oPaging.iLength;
							fnDraw( oSettings );
						} );
				}

				// Add / remove disabled classes from the static elements
				if ( oPaging.iPage === 0 ) {
					$('li:first', an[i]).addClass('disabled');
				} else {
					$('li:first', an[i]).removeClass('disabled');
				}

				if ( oPaging.iPage === oPaging.iTotalPages-1 || oPaging.iTotalPages === 0 ) {
					$('li:last', an[i]).addClass('disabled');
				} else {
					$('li:last', an[i]).removeClass('disabled');
				}
			}
		}
	}
} );



    var datatable = $('#${datatable.eid}').dataTable(${options});

    % if datatable.search == 'col':
    $('.dataTables_filter').hide();
    % endif

    $("div.dt-toolbar").html('${datatable.toolbar()}');

    $('#searchCol').change(function(){datatable.fnFilter($('.dataTables_filter input').val())});

    % if datatable.show_details:
    $('#${datatable.eid} tbody td span').live( 'click', function () {
        var nTr = $(this).parents('tr')[0];
        if (datatable.fnIsOpen(nTr))
        {
            /* This row is already open - close it */
            $(this).attr('class', 'ui-icon ui-icon-circle-plus');
            datatable.fnClose( nTr );
        }
        else
        {
            $(this).attr('class', 'ui-icon ui-icon-circle-minus');
            $.get($(this).attr('href'), {}, function(data, textStatus, jqXHR) {
                datatable.fnOpen( nTr, data, 'details' );
            }, 'html');
            /* Open this row */
        }
    } );
    % endif

    $("tfoot input").keyup( function () {
        /* Filter on the column (the index) of this element */
        datatable.fnFilter(this.value, $("tfoot .control").index(this));
    } );

	$("tfoot select").change( function () {
        /* Filter on the column (the index) of this element */
        datatable.fnFilter($(this).val(), $("tfoot .control").index(this));
    } );
} );
</script>
