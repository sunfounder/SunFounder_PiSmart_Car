onmessage = function (cmd){
    if (cmd != ''){
      action(cmd);
      cmd = '';
    }
 }