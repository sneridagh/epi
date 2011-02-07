controlStatus = 'up'
function consultarPresencia()
{
persones = ''
$.ajax({
  url: 'consultarPresencia',
  data: {},
  success: function(data){
   persones = $.parseJSON(data);
        $("#consulta").autocomplete(persones, {
            minChars: 0,
            width: 350,
            matchContains: true,
            highlightItem: false,
            max:200,
            multiple:true,
            multipleSeparator:' ',
            scrollHeight:400,
            formatItem: function(row, i, max, term) {
                    restat=''
                    if (row.online)
                       { restat= '<img src="/images/online.gif">  '}
                    else
                       { restat= '<span style="display:none" class="offline"></span>'}
                    rli = restat+"<strong>"+row.nom+"</strong> - <span style='font-size: 80%;'>" + row.equip + "</span><br>"
                    rli = rli + "<span style='font-size: 89%;'>Intern: " + row.intern + "</span>"
                    if (row.mobil.length>0)
                      {rli = rli + ", <span style='font-size: 90%;'>Mòbil: " + row.mobil + "</span>";}

	            return rli;
            },
            formatResult: function(row) {
	            return row.to;
            }
        });
 $('#consulta').val('Cerca persones o telèfons...')
 }
});

}

      String.prototype.format = function(){
      var pattern = /\{\d+\}/g;
      var args = arguments;
      return this.replace(pattern, function(capture){ return args[capture.match(/\d+/)]; });
      };

    $(document).ajaxStart(function(){
         $('#ajaxWorking').show();
    }).ajaxStop(function(){
         $('#ajaxWorking').hide();
    });

	$(function() {
	    $(document).keydown(function(event){
	        controlStatus = 'down';
	    });
	    $(document).keyup(function(event){
	        controlStatus = 'up';

	    });
        consultarPresencia();

		
		
		$(".motiu").draggable({helper:'clone', opacity: 0.7});
		$(".especials").droppable({
		    hoverClass : 'dragginghover',
		    accept: '.motiu',
			drop: function(event, ui)
			   {
 			   lastimg = $(this).find('img:last');

			    newimg = '<img src="'+ui.draggable.attr('src')+'" title="'+ui.draggable.attr('title')+'">';
                if (lastimg.length==0)
                  {
                  $(this).html(newimg);
                  }
                else
                  {
                   lastimg.after(newimg);
                  }
 			   

			   }
		    });		
		
		$(".imputacio").draggable({helper:'clone', opacity: 0.7});
		$(".llistaimputacions").droppable({
		    hoverClass : 'dragginghover',
		    accept: 'li',
			drop: function(event, ui) {
				lastli = $(this).find('li:last');
                if (lastli.length==0)
                  {
                    classe='imputacio';
                  }
                else
                  {
                    if (lastli.hasClass('odd'))
                      { classe='imputacio';}
                    else
                      { classe='imputacio odd';}
                  }
                newli = '<li class="'+classe+'">'+ui.draggable.html()+'</li>';

                if (lastli.length==0)
                  {
                  $(this).html(newli);
                  }
                else
                  {
                   lastli.after(newli);
                  }
                $(this).find('li:last').draggable({helper:'clone', opacity: 0.7});
                parent_of_draggable = ui.draggable.parent()
                //ui.draggable.remove();
                if (parent_of_draggable.find('li').length==1)
                  {parent_of_draggable.html('<span class="noimputacions">No hi ha imputacions</span')}
                ui.helper.remove();
                iid = ui.draggable.find('.amount div').attr('id');
                amount = ui.draggable.find('.amount span').text();
                newdate = $(this).attr('id')
                if (controlStatus=='up')
                  {
                    $.get('moureImputacio', {amount:amount,iid:iid,newdate:newdate}, function(data){
                       ui.draggable.remove();
                       },'json');
                  }
                else
                  {
                    $.get('copiarImputacio', {amount:amount,iid:iid,newdate:newdate}, function(data){
                       },'json');
                  }
			}
		});

	});

  function marcarPresencia()
    {
     $.get('marcarPresencia', {}, function(data){
         $('#header').html(data);
         consultarPresencia();
           });
    }

  function toggleCodiLlista()
    {
    $('#imputacio_codi').toggle();
    $('#imputacio_llista').toggle();

    }

  function imputacioTiquetFancybox(dia)
    {
      $.get('finestraImputacio', {dia:dia}, function(data){
            $.fancybox( data,
                   { 'autoDimensions' : true,
                     'scrolling'        : 'no',
                   }
                 );

            });
    }

  function time_inc_consolidate(digit)
    {
       if (digit=='m1')
         {time_inc('m0')}
       if (digit=='m0')
         {time_inc('h1')}
       if (digit=='h1')
         {time_inc('h0')}

    }

  function time_dec_consolidate(digit)
    {
       if (digit=='m1')
         {time_dec('m0')}
       if (digit=='m0')
         {time_dec('h1')}
       if (digit=='h1')
         {time_dec('h0')}

    }


  function time_inc(digit)
    {
       var max = 9
       if (digit=='m0')
          {max = 5}
       var num = parseInt($("#"+digit).attr('value'));
       var nnum = 0;
       if (num!=max)
         { nnum = num+1}
       else
         { time_inc_consolidate(digit)}
       $("#"+digit).attr('value',nnum.toString());

    }

  function time_dec(digit)
    {
       var max = 9
       if (digit=='m0')
          {max = 5}

       var num = parseInt($("#"+digit).attr('value'));
       var nnum = max;
       if (num!=0)
         { nnum = num-1}
       else
         { time_dec_consolidate(digit)}

       $("#"+digit).attr('value',nnum.toString());
    }

  function modificarImputacioFancybox(iid,h0,h1,m0,m1)
    {

      data = '<div id="modificaciofancy">';
      data+= '<div><h3>Modificar Imputació</h3>'
      data+= '<span>Utilitza les fletxetes per modificar el temps, i la caixa de text per posar un comentari a la imputació </span></div><br/>';
      data+= '<div style="float:left;">'
      data+= '<table>';
      data+= '<tr>'
      data+= '  <td><img src="/images/arrowup.png" onclick="time_inc('+"'h0'"+')"></td>'
      data+= '  <td><img src="/images/arrowup.png" onclick="time_inc('+"'h1'"+')"></td>'
      data+= '  <td></td>'
      data+= '  <td><img src="/images/arrowup.png" onclick="time_inc('+"'m0'"+')"></td> '
      data+= '  <td><img src="/images/arrowup.png" onclick="time_inc('+"'m1'"+')"></td>  '
      data+= '</tr>';
      data+= '<tr>'
      data+= '  <td><input id="h0" name="h0" class="digit" type="text" value="'+h0+'"></td>'
      data+= '  <td><input id="h1" name="h1" class="digit" type="text" value="'+h1+'"></td>'
      data+= '  <td style="font-size:20px;">:</td>'
      data+= '  <td><input id="m0" name="m0" class="digit" type="text" value="'+m0+'"></td>'
      data+= '  <td><input id="m1" name="m1" class="digit" type="text" value="'+m1+'"></td>'
      data+= '</tr>';
      data+= '<tr>'
      data+= '  <td><img src="/images/arrowdown.png" onclick="time_dec('+"'h0'"+')"></td>'
      data+= '  <td><img src="/images/arrowdown.png" onclick="time_dec('+"'h1'"+')"></td>'
      data+= '  <td></td>'
      data+= '  <td><img src="/images/arrowdown.png" onclick="time_dec('+"'m0'"+')"></td> '
      data+= '  <td><img src="/images/arrowdown.png" onclick="time_dec('+"'m1'"+')"></td>  '
      data+= '</tr>';
      data+= '</table>';
      data+= '</div>'
      data+= '<div style="margin-left:15px;text-align:right;">'
      data+= '<textarea style="width:300px;height:80px;" id="micomment" name="micomment">Carregant comentari...</textarea>'
      data+= '<input type="button" value="Guardar" onclick="saveModificarImputacio('+"'"+iid+"'"+')">'
      data+= '</div>'
      data+= '<input type="hidden" name="hold" id="hold" value="'+h0+h1+'">';
      data+= '<input type="hidden" name="mold" id="mold" value="'+m0+m1+'">';


      data+= '</div>';

        $.fancybox( data,
               { 'autoDimensions' : true,
                 'scrolling'        : 'no',
               }
             );
      $.get('comentariImputacio', {iid:iid.replace('iid-','')}, function(data){
             $('#micomment').val(data)
            });




    }



  function modificarMarcatgeFancybox(url)
    {

      data = '<div id="marcatgesfancy">';
      data+= '<div><h3>Modificar Marcatges</h3>'
      data+= '<span>Redimensiona les caixes per canviar el valor de la imputació </span></div><br/>';
      data+= '';
      data+= '<div id="contenidor_marcatges">'
      data+= '<div id="per0" class="periode" style="left:14;width:40;"><span class="drg start" style="left:0;"></span></div>'
      data+= '<div id="per1" class="periode" style="left:55;width:80;"><span class="drg end" style="left:0;"></span></div>'
      data+= ''
      data+= ''
      data+= ''
      data+= '</div>'

      $.fancybox( data,
           { 'autoDimensions' : true,
             'scrolling'        : 'no',
           }
         );


      $( "#per0 .drg" ).draggable({
        grid: [ 2,2 ],
        axis: "x",
        containment: "parent",

      });


      $( "#per1 .drg" ).draggable({
        grid: [ 2,2 ],
        axis: "x",
        containment: "parent"
      });


    }

  function toggleSetmana(setmana)
    {
      $('#setmana-'+setmana+' .boxbody').slideToggle('slow')
    };

  function togglePermisosBox()
    {
      $('#permisos .box').slideToggle('fast')
    };


  function actualitzarMarcadors(dia,marcades,aimputar,imputades,pendents)
     {
      $('#tr-'+dia+' .treballades span').text(marcades)
      $('#tr-'+dia+' .aimputar span').text(aimputar)
      $('#tr-'+dia+' .imputades span').text(imputades)
      $('#tr-'+dia+' .pendents span').text(pendents)
     }

  function esborrarImputacio(img,dia,iid)
    {
       li = $(img).parent().parent();
       span = $('#iid-'+iid+' span');
       text = span.text();
       hm = text.split(':');
       $.get('esborrarImputacio', { dia:dia, iid:iid, hores:hm[0], minuts:hm[1]}, function(data){
          actualitzarMarcadors(dia,data['marcades'],data['aimputar'],data['imputades'],data['pendents']);
          li.remove();
       },'json');

    }

  function imputarAjax(dia, tipus)
    {
     opcio = $('#novaimputacio'+tipus+'-'+dia).find("select[name='seleccio']").val();
     hores = $('#novaimputacio'+tipus+'-'+dia).find("input[name='hores']").val();
     if (hores.length==0) {hores='00';}
     minuts = $('#novaimputacio'+tipus+'-'+dia).find("input[name='minuts']").val();
     if (minuts.length==0) {minuts='00';}

     if ((opcio!=0) & !(hores=='00' & minuts=='00'))
     {
         $.get('crearImputacio', {hores:hores, dia:dia, minuts:minuts, opcio:opcio, tipus:tipus}, function(data){
            if (data['confirm']=='ok')
              {
                lastli = $('#imputacions-'+dia+' li:last');
                if (lastli.length==0)
                  {
                    classe='imputacio';
                    ul = $('#imputacions-'+dia);
                  }
                else
                  {
                    if (lastli.hasClass('odd'))
                      { classe='imputacio';}
                    else
                      { classe='imputacio odd';}
                  }
                iid=data['code'];
                titol= $('#novaimputacio'+tipus+'-'+dia+' #seleccio option[value='+opcio+']').text();

                newli ='<li class="'+classe+'">';
                newli+='  <div class="amount">';
                newli+='     <div id="iid-'+iid+'">';
                newli+='         <span>'+data['hores']+':'+data['minuts']+'</span>';
                newli+='     </div>';
                newli+='  </div>';
                newli+='  <div class="concepte">';
                newli+='      <a target="_blank" href="https://maul.upc.es:8444/imputacions/control/imputacioDetall?timeEntryId='+iid+'">'+titol+'</a>';
                newli+='  </div>';
                newli+='  <div class="accions">';
                newli+='      <img onclick="toggleModificarImputacio('+"'"+'iid-'+iid+"'"+')" src="/images/pencil.gif"/>';
                newli+='      <img onclick="esborrarImputacio(this,'+"'"+dia+"','"+iid+"'"+')" src="/images/esborrar.gif"/>';
                newli+='  </div>';
                newli+='</li>';
                if (lastli.length==0)
                  {
                  ul.html(newli);
                  }
                else
                  {
                   lastli.after(newli);
                  }
                actualitzarMarcadors(dia,data['marcades'],data['aimputar'],data['imputades'],data['pendents'])
                $('#novaimputacio'+tipus+'-'+dia).find("input[name='hores']").val('');
                $('#novaimputacio'+tipus+'-'+dia).find("input[name='minuts']").val('');

              }
            else
              {
                alert(data['code']);
              }

           },'json');
     }
    else
     {
      alert('No pots deixar les opcions buides!!!');
     }
    }
  function toggleNovesImputacions(dia)
    {
      $('#ni-'+dia).toggle('fast');
    }

  function toggleModificarImputacioKeyPress(e,input)
    {
      if (e.keyCode == 13) {saveModificarImputacio(input,'ok')}
      if (e.keyCode == 27) {saveModificarImputacio(input,'cancel')}
    }

  function toggleModificarImputacio(iid)
    {
      div = $('#'+iid);
      span = $('#'+iid+' span');
      text = span.text();
      hm = text.split(':');
      h = hm[0]
      m = hm[1]

      if (h.length==1)
         {h = '0'+h;}
      modificarImputacioFancybox(iid,h[0],h[1],m[0],m[1])


    };

  function toggleModificarMarcatge(marcatgeUrl)
    {
      modificarMarcatgeFancybox(marcatgeUrl)

    };

  function saveModificarImputacio(iid)
    {
       div = $('#'+iid);
       span = $('#'+iid+' span');
       h0 = $('#h0').attr('value');
       h1 = $('#h1').attr('value');
       m0 = $('#m0').attr('value');
       m1 = $('#m1').attr('value');
       hold = $('#hold').attr('value');
       mold = $('#mold').attr('value');
       dia = div.parent().parent().parent().attr('id').replace('imputacions-','')
       comentari =  $('#micomment').val()


//       if (h0!='0')
//          {span.text(h0+h1+':'+m0+m1);}
//       else
//          {span.text(h1+':'+m0+m1);}
       $.get('modificarTempsImputacio', {comentari:comentari,hores:h0+h1, minuts:m0+m1, horesold:hold, minutsold:mold, iid:iid.replace('iid-',''), dia:dia}, function(data){
         actualitzarMarcadors(dia,data['marcades'],data['aimputar'],data['imputades'],data['pendents']);
         div.replaceWith('<div id="'+iid+'"><span onclick="toggleModificarImputacio(\''+iid+'\')">'+data['hores']+':'+data['minuts']+'</span></div>');
       }, 'json');

       $.fancybox.close()

    }
