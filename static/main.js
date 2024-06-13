import { $ } from "/static/jquery/src/jquery.js";

// export function say_hi(elt) {
//     console.log("Say hi to", elt);
// }
// say_hi($("h1"));

export function make_table_sortable(table)
{
    let THs = $(table).find("thead").find("tr").children()
    
    let DueDateHeader = null
    if(THs.length>2 && THs[THs.length-2].innerText == "Due Date")
        DueDateHeader = THs[THs.length-2]
        
    // let lastHeader = THs[THs.length - 1]
    // I know that there is an easier way to do this (^^^^), but this ensures it selectin a <th> element
    let lastChild = null
    for(let i = 0; i < THs.length; i++)
    {
        if($(THs[i]).is("th"))
        lastChild = THs[i]
    }

    //  score/weight click handler
    $(lastChild).on("click", function() {

        //if the table is currently being sorted by due date, unsort and remove class tags
        let tbody = $(table).find("tbody")
        let tableRows = $(tbody).find("tr")
        let rowArray = $(tableRows).toArray()
        rowArray.sort(unsort)
        $(rowArray).appendTo(tbody)
        if($(DueDateHeader).hasClass("sort-desc") === true)
            $(DueDateHeader).removeClass("sort-desc")
        if($(DueDateHeader).hasClass("sort-asc") === true)
            $(DueDateHeader).removeClass("sort-asc")




                //case: hasn't been clicked yet
        if($(lastChild).hasClass("sort-asc") === false && $(lastChild).hasClass("sort-desc") === false)
        {
            console.log("sorting by ascending order")
            $(lastChild).addClass("sort-asc")
            
            //sort ascending
            let tbody = $(table).find("tbody")
            let tableRows = $(tbody).find("tr")
            let rowArray = $(tableRows).toArray()
            rowArray.sort(compareAscending)

            $(rowArray).appendTo(tbody)
        } 
        else    //case: has been clicked and is already sorting by ascending
        if($(lastChild).hasClass("sort-asc") === true)
        {
            console.log("now sorting by descending order")
            $(lastChild).removeClass("sort-asc")
            $(lastChild).addClass("sort-desc")

            //sort descending
            let tbody = $(table).find("tbody")
            let tableRows = $(tbody).find("tr")
            let rowArray = $(tableRows).toArray()
            rowArray.sort(compareDescending)

            $(rowArray).appendTo(tbody)

        }
        else    //case: has been clicked and is already sorting by descending
        if($(lastChild).hasClass("sort-desc") === true)
        {
            console.log("returning to initial order")
            $(lastChild).removeClass("sort-desc")

            //change to unsorted
            let tbody = $(table).find("tbody")
            let tableRows = $(tbody).find("tr")
            let rowArray = $(tableRows).toArray()
            rowArray.sort(unsort)
            $(rowArray).appendTo(tbody)

        }

    })

    //  Due Date click handler
    if(DueDateHeader !== null){
        
        $(DueDateHeader).on("click", function() {

            //if the rows are already sorted by a different column, unsort them
            let tbody = $(table).find("tbody")
            let tableRows = $(tbody).find("tr")
            let rowArray = $(tableRows).toArray()
            rowArray.sort(unsort)
            $(rowArray).appendTo(tbody)
            if($(lastChild).hasClass("sort-desc") === true)
                $(lastChild).removeClass("sort-desc")
            if($(lastChild).hasClass("sort-asc") === true)
                $(lastChild).removeClass("sort-asc")



                    //case hasn't been sorted yet, sort by ascending
            if($(DueDateHeader).hasClass("sort-asc") === false && $(DueDateHeader).hasClass("sort-desc") === false)
            {
                $(DueDateHeader).addClass("sort-asc")
                console.log("sort due date by asc")

                //sort ascending
                let tbody = $(table).find("tbody")
                let tableRows = $(tbody).find("tr")
                let rowArray = $(tableRows).toArray()
                rowArray.sort(compareDueDateAscending)
                $(rowArray).appendTo(tbody)

            }
            else    //case has been clicked, sort by descending
            if($(DueDateHeader).hasClass("sort-asc") === true)
            {
                $(DueDateHeader).removeClass("sort-asc")
                $(DueDateHeader).addClass("sort-desc")
                console.log("sort due date by desc")

                //sort descending
                let tbody = $(table).find("tbody")
                let tableRows = $(tbody).find("tr")
                let rowArray = $(tableRows).toArray()
                rowArray.sort(compareDueDateDescending)
                $(rowArray).appendTo(tbody)
            }
            else    //case has been clicked, is sorted by descending, reset
            if($(DueDateHeader).hasClass("sort-desc") === true)
            {
                $(DueDateHeader).removeClass("sort-desc")
                console.log("reset due date sort")

                //change to unsorted
                let tbody = $(table).find("tbody")
                let tableRows = $(tbody).find("tr")
                let rowArray = $(tableRows).toArray()
                rowArray.sort(unsort)
                $(rowArray).appendTo(tbody)
            }

        })
    }
}
//helper function for make_table_sortable
function compareDescending(a, b)
{
    let childrenA = $(a).children()
    let lastTDa = null
    for(let i = 0; i < childrenA.length; i++)
    {
        if($(childrenA[i]).is("td"))
            lastTDa = childrenA[i]
    }
    let valueA = parseFloat(lastTDa.innerText)



    let childrenB = $(b).children()
    let lastTDb = null
    for(let i = 0; i < childrenB.length; i++)
    {
        if($(childrenB[i]).is("td"))
            lastTDb = childrenB[i]
    }
    let valueB = parseFloat(lastTDb.innerText)

    if(valueA > valueB || isNaN(valueB) === true)
        return 1
    if(valueB > valueA || isNaN(valueA) === true)
        return -1
    
    return 0
}

//helper function for make_table_sortable
function compareAscending(a, b)
{
    let childrenA = $(a).children()
    let lastTDa = null
    for(let i = 0; i < childrenA.length; i++)
    {
        if($(childrenA[i]).is("td"))
            lastTDa = childrenA[i]
    }
    let valueA = parseFloat(lastTDa.innerText)



    let childrenB = $(b).children()
    let lastTDb = null
    for(let i = 0; i < childrenB.length; i++)
    {
        if($(childrenB[i]).is("td"))
            lastTDb = childrenB[i]
    }
    let valueB = parseFloat(lastTDb.innerText)
    
    if(valueA < valueB || isNaN(valueA) === true)
        return 1
    if(valueB < valueA || isNaN(valueB) === true)
        return -1
    
    return 0
}

function compareDueDateAscending(a, b)
{
    // let childrenA = $(a).children()
    // let childA = $(childrenA[1]).data("value")
    // let childrenB = $(b).children()
    // let childB = $(childrenB[1]).data("value")

    let A = $(($(a).children())[1]).data("value")
    let B = $(($(b).children())[1]).data("value")
    
    if(A > B)
        return 1
    if(A < B)
        return -1
    return 0
}

function compareDueDateDescending(a, b)
{
    // let childrenA = $(a).children()
    // let childA = $(childrenA[1]).data("value")
    // let childrenB = $(b).children()
    // let childB = $(childrenB[1]).data("value")

    let A = $(($(a).children())[1]).data("value")
    let B = $(($(b).children())[1]).data("value")
    
    if(A < B)
        return 1
    if(A > B)
        return -1
    return 0
}


function unsort(a,b)
{
    if($(a).data("index") > $(b).data("index"))
        return 1
    if($(a).data("index") < $(b).data("index"))
        return -1
   
    return 0
}


export function make_form_async(form)
{

$(form).on("submit", function( event ){
    //stop form from submitting
    event.preventDefault()
    //disable file changing
    let fileInput = $(form).find("input")
    fileInput.disabled=true
    //disable submission button
    let button = $(form).find("button")
    button.disabled = true

    //make the form
    let formdata = new FormData($(form)[0])

    //submit the form
    $.ajax({
        url: form[0].action, 
        method: "POST",
        data: formdata, 
        processData: false,
        contentType: false,
        mimeType: form[0].enctype,
        success: function (response) {
            $(form).replaceWith("<p>Upload succeeded</p>")
        },
        failure: function (response) {console.log("uh oh, there was a problem with your submission")}
    })

})
}

export function make_grade_hypothesized(table)
{
    let button = $("<button class='btn btn-primary' id='grade-hypothesized'>Hypothesize</button>")
    $(table).before(button)
    $(button).on("click", function(){

        if($(table).hasClass("hypothesized") === false)
        {
            computeCurrentGrade(table)
            $(table).addClass("hypothesized")
            $(button).text("Actual Grades")

            let tds = $(table).find("td")
            for(let i = 0; i < tds.length; i++)
            {
                if(tds[i].innerText === "Not Due" || tds[i].innerText === "Ungraded")
                {
                    $(tds[i]).data("value", tds[i].innerText)
                    $(tds[i]).addClass("newInput")
                    let hypothesizedGradeInput = $("<input type='number' step='0.01'></input>")
                    $(tds[i]).text("")
                    $(tds[i]).append(hypothesizedGradeInput)
                }
            }
            $('.newInput').on("change", function(){
                computeCurrentGrade(table)
            })
        }
        else
        { 
            $(table).removeClass("hypothesized")
            $(button).text("Hypothesize")
            
            let tds = $(table).find("td")
            for(let i = 0; i < tds.length; i++)
            {
                if($(tds[i]).data("value") !== undefined)
                {
                    $(tds[i]).text($(tds[i]).data("value"))
                }
            }
            computeCurrentGrade(table)
        }
        
    })

}

function computeCurrentGrade(table)
{
    let totalWeight = 0
    let totalEarned = 0

    let tds = $(table).find("td")
    for(let i = 0; i < tds.length; i++)
    {
        if($(tds[i]).text() === "Missing")
        {
            totalWeight += $(tds[i]).data("weight")
        }
        else
        if(parseFloat($(tds[i]).text()) >= 0)
        {
            totalWeight += $(tds[i]).data("weight")
            totalEarned += $(tds[i]).data("weight") * (parseFloat($(tds[i]).text())/100)
        }
        else
        if($(tds[i]).hasClass("newInput"))
        {
            if(parseFloat($($(tds[i]).find('input')).val()))
            {
                totalWeight += $(tds[i]).data("weight") 
                totalEarned += $(tds[i]).data("weight") * (parseFloat($($(tds[i]).find('input')).val())/100)
            }
        }
            
    }

    let footerTHs = $(($(table).find("tfoot"))).find("th")
    for(let i = 0; i < footerTHs.length; i++)
    {
        if($(footerTHs[i]).hasClass("numberColumn") === true)
        {
            $(footerTHs[i]).text((Math.round((totalEarned/totalWeight)*10000))/100 + "%")
        }
            
    }


}
