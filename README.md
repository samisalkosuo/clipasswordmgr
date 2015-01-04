clipasswordmgr
==============

Command Line Password Manager is a tool to manage passwords in the shell.

Commands:
<pre>
   add                                                                               Add new account.                                          
   changepassphrase                                                                  Change passphrase.                                        
   debug            on|off                                                           Print or don't print debug info.                          
   delete           &lt;start of name>                                                  Delete account(s) that match given string.                
   exit                                                                              Exit program.                                             
   exportjson       &lt;filename>                                                       Export accounts as JSON to a file.                        
   help                                                                              This help.                                                
   list             [&lt;start of name> | json]                                         Print all or given accounts. If json is given, print JSON.
   loadjson         &lt;filename>                                                       Load accounts from file. Overrides any existing accounts. 
   meta                                                                              View meta data.                                           
   metaset          &lt;key> &lt;value>                                                    Set key:value to JSON meta data.                          
   modify           &lt;start of name>                                                  Modify account(s).                                        
   pwd              [&lt;number of pwds>] [&lt;pwd length>]                                Generate password(s).                                     
   search           &lt;string in name or comment> | 
                    username=&lt;string> | 
                    email=&lt;string> Search accounts that have matching string.                
   select           &lt;rest of select SQL>                                             Execute SELECT SQL.                                       
   view             &lt;start of name>                                                  View account(s) details.
</pre>

Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
