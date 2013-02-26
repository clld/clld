<%namespace name="util" file="../util.mako"/>

${h.rendered_sentence(ctx)}

<script>
$(document).ready(function() {
    $('.ttip').tooltip({placement: 'bottom', delay: {hide: 300}});
});
</script>
