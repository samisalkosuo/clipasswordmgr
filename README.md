clipasswordmgr
==============

Command Line Password Manager is a tool to manage passwords in the shell.

Commands:
   add                                                                               Add new account.                                          
   changepassphrase                                                                  Change passphrase.                                        
   debug            on|off                                                           Print or don't print debug info.                          
   delete           <start of name>                                                  Delete account(s) that match given string.                
   exit                                                                              Exit program.                                             
   exportjson       <filename>                                                       Export accounts as JSON to a file.                        
   help                                                                              This help.                                                
   list             [<start of name> | json]                                         Print all or given accounts. If json is given, print JSON.
   loadjson         <filename>                                                       Load accounts from file. Overrides any existing accounts. 
   meta                                                                              View meta data.                                           
   metaset          <key> <value>                                                    Set key:value to JSON meta data.                          
   modify           <start of name>                                                  Modify account(s).                                        
   pwd              [<number of pwds>] [<pwd length>]                                Generate password(s).                                     
   search           <string in name or comment> | username=<string> | email=<string> Search accounts that have matching string.                
   select           <rest of select SQL>                                             Execute SELECT SQL.                                       
   view             <start of name>                                                  View account(s) details.


Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
