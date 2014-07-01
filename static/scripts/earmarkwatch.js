function flagAnswer(ans_id) {
    // issue AJAX request to 'flag-answer/'+id
    new Ajax.Request(
        '/flag-answer/'+ans_id+'/',
        {
            method: 'post',
            onSuccess: function(request) {
                var flaglink = $('flagquestion'+ans_id);
                flaglink.innerHTML = 'flagged';
                flaglink.className = 'flagged';
                $('answer'+ans_id).className = 'answerbox_flagged';
            }
        });
}

function flagAddress(street, city, state, zip) {
    if(street) {
        flagAnswer(street);
    }
    if(city) {
        flagAnswer(city);
    }
    if(state) {
        flagAnswer(state);
    }
    if(zip) {
        flagAnswer(zip);
    }
    var flaglink = $('flagaddress');
    flaglink.innerHTML = 'flagged';
    flaglink.className = 'flagged';
    $('answeraddress').className = 'answerbox_flagged';
}


function flagAllAnswers(eid) {
    new Ajax.Request(
        '/flag-answers-for/'+eid+'/',
        {
            method: 'post',
            onSuccess: function(request) {
                var ids = eval(request.responseText);
                for(var i=0; i < ids.length; ++i) {
                    var x = $('flagquestion'+ids[i]);
                    if(x) {
                        x.innerHTML = 'flagged';
                        x.className = 'flagged';
                        $('answer'+ids[i]).className = 'answerbox_flagged';
                    }
                }
            }
        });
}

function flagComment(id) {
    // issue AJAX request to 'flag-comment/'+id
    new Ajax.Request(
        '/flag-comment/'+id+'/',
        {
            method: 'post',
            onSuccess: function(request) {
                var flaglink = $('flagcomment'+id);
                flaglink.innerHTML = 'flagged';
                flaglink.className = 'flagged';
            }
        });
}

function show_url_input(e) {
	$(Event.element(e).id.replace('_yes','_url_entry')).show();
	$(Event.element(e).id.replace('_yes','_url')).value = '';
}

function hide_url_input(e) {
	$(Event.element(e).id.replace('_no','_url_entry')).hide();
	$(Event.element(e).id.replace('_no','_url')).value = 'N/A';
}

function add_url_toggle_events(idprefix) {
	Event.observe(idprefix+'_yes', 'click', show_url_input);
	Event.observe(idprefix+'_no',  'click', hide_url_input);
}
