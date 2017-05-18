	
$(document).ready(function() {
   $('#calendar').fullCalendar({
        monthNames:["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
        dayNamesShort:["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
        events: [
        {% for week in month_days %}
            {% for day, entries, current in week %}
                {% if day != 0 %}
                        {% for entry in entries %}
                            {
                                title: "{{ entry.horaInicio|date:"H:i" }}-{{ entry.horaFim|date:"H:i" }}",
                                start: "{{entry.data|date:"Y-m-d"}}"
                            },
                        {% endfor %}
                {% endif %}
            {% endfor %}
        {% endfor %}
        ],
        eventAfterAllRender: function() {
            $(".fc-day-top").each(function(index,value) {                  
                $(value).html("<a id='addReserva' href='#modal1'><i class='left material-icons'>add</i></a> <span class='fc-day-number'>"+$(value).find("span").html()+ "</span>");
           });
        }
    });     
    setMonth();
});

function setMonth() {
    if({{month}}>9) {
        var date = $.fullCalendar.moment("{{year}}-{{month}}-01");
            $("#calendar").fullCalendar('gotoDate', date);
    } else {
        var date = $.fullCalendar.moment("{{year}}-0{{month}}-01");
            $("#calendar").fullCalendar('gotoDate', date);
        }
}
