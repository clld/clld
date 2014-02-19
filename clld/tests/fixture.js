
google = {
    feeds: {
        Feed: function(){
            return {
                setNumEntries: function(){},
                load: function(f){
                    f({feed: {title: 't', entries: [{title: 'e'}]}});
                }
            }
        }
    }
};

document = {
    location: {href: null}
};
