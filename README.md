clipasswordmgr
==============

Command Line Password Manager is a tool to manage passwords in the command line. All accounts/passwords are stored in an encrypted file, protected by user given passphrase.

Encryption/decryption is done using Python cryptography library: https://cryptography.io/en/latest/

Commands:
<table width="100%">
<tr>
<td width="20%">add</td>
<td width="30%">&nbsp;</td>
<td width="50%">Add new account.</td>
</tr>

<tr>
<td width="20%">changepassphrase</td>
<td width="30%">&nbsp;</td>
<td width="50%">Change passphrase.</td>
</tr>
                                                                                  
<tr>
<td width="20%">debug</td>
<td width="30%">on|off</td>
<td width="50%">Print or don't print debug info.</td>
</tr>
                                                                     
<tr>
<td width="20%">delete</td>
<td width="30%">&lt;start of name></td>
<td width="50%">Delete account(s) that match given string.</td>
</tr>
                                                                          
<tr>
<td width="20%">exit</td>
<td width="30%">&nbsp;</td>
<td width="50%">Exit program.</td>
</tr>
                                                                
<tr>
<td width="20%">exportjson</td>
<td width="30%">&lt;filename></td>
<td width="50%">Export accounts as JSON to a file.</td>
</tr>
                                                                
<tr>
<td width="20%">help</td>
<td width="30%">&nbsp;</td>
<td width="50%">This help.</td>
</tr>
                                                                                                               
<tr>
<td width="20%">list</td>
<td width="30%">[&lt;start of name> | json]</td>
<td width="50%">Print all or given accounts. If json is given, print JSON.</td>
</tr>
                                                         
<tr>
<td width="20%">loadjson</td>
<td width="30%">&lt;filename></td>
<td width="50%">Load accounts from file. Overrides any existing accounts.</td>
</tr>

<tr>
<td width="20%">meta</td>
<td width="30%">&nbsp;</td>
<td width="50%">View meta data.</td>
</tr>
            
<tr>
<td width="20%">metaset</td>
<td width="30%">&lt;key> &lt;value></td>
<td width="50%">Set key:value to JSON meta data.</td>
</tr>
                                                                                 
<tr>
<td width="20%">modify</td>
<td width="30%">&lt;start of name></td>
<td width="50%">Modify account(s).</td>
</tr>
                                                                 
<tr>
<td width="20%">pwd</td>
<td width="30%">[&lt;number of pwds>] [&lt;pwd length>]</td>
<td width="50%">Generate password(s).</td>
</tr>
                                                                
<tr>
<td width="20%">search</td>
<td width="30%">&lt;string in name or comment> | username=&lt;string> | email=&lt;string></td>
<td width="50%">Search accounts that have matching string.</td>
</tr>
   
<tr>
<td width="20%">select</td>
<td width="30%">&lt;rest of select SQL></td>
<td width="50%">Execute SELECT SQL.</td>
</tr>
               
<tr>
<td width="20%">view</td>
<td width="30%">&lt;start of name></td>
<td width="50%">View account(s) details.</td>
</tr>

</table>
                                                           
                                                              

Some words about the origins of CLI Password Manager: http://sami.salkosuo.net/cli-password-manager/
