#! /usr/bin/env python

"""
Copyright 2014 Hans Hoogenboom

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os, sys

# TODO: export/output of parms????

# metadata according to the OSL specification
_shaderTypes = ["surface", "displacement", "light", "volume", "shader"]
_shaderKeys  = ["name", "label", "type", "help", "url", "value", "page", "widget", "float", "int", "units"]
_parmWidgets = ["number", "string", "boolean", "checkBox", "popup", "mapper", "filename", "null"]
_parmFloat   = ["min", "max", "sensitivity"]
_parmInteger = ["min", "max", "sensitivity", "digits", "slider"]
_parmKeyword = ["output"]


def _error( msg, crash = False ):
    sys.stderr.write( msg )
    sys.stderr.write( '\n' )
    if crash:
        sys.exit(1)
    return False


def _formatVal( st ):
    value = st.replace('"','',2)
    value = value.strip()
    return value


def _getKeyValue( st ):
    signPos = st.index('=')
    value   = st[signPos+1:]
    key     = st[:signPos-1]
    key     = key.split()
    key     = key[-1].strip()
    return (key, value)


def parseOslInfo( compiledShader ):
    DEBUG = False

    try:
        cmd = 'oslinfo -v %s' % compiledShader
        fp = os.popen(cmd, 'r')
    except:
        _error("Invalid shaders in file %s.\n" % compileShader)
        return False

    lines = fp.readlines()
    if not lines:
        _error('Missing shader definition for %s' % compiledShader)
        return False
    count = 0
    shaderDef = lines[ count ]    
    args = shaderDef.split()

    # tempShader stores all the data
    tempShader = dict()
    # stores the order in which oslinfo outputs its data
    # and separates the parameters from general shader data
    parmlist = list()
    if args[0] not in _shaderTypes:
        _error("Not a valid shader type: %s" % args[0])
        return False
    else:
        tempShader['type'] = _formatVal( args[0] )
        tempShader['name'] = _formatVal( args[1] ) 
        tempShader['hasMetaData'] = False
        tempShader['hasParmHelp'] = False
        
    # parse the rest of the file to get parameters
    # number of entries in lines
    length = len( lines ) - 1
    # lines iterator
    count = 1
    while True:
        line = lines[ count ]
        if not line:
            _error( "No more lines to read, invalid shader %s?" % compiledShader )
        args = line.split()

        # find parameter name
        if args[0] not in ["Default", "metadata:"]: # or args[0] == "export":
            tempparm = dict()
            if len( args ) < 3:
                tempparm['name'] = _formatVal( args[0] )
                tempparm['type'] = _formatVal( args[1] )
            else:
                tempparm['output'] = True
                tempparm['name']   = _formatVal( args[0] )
                tempparm['type']   = _formatVal( args[2] )
            condition = True
            widget = list()
            while condition:
                # read next line
                count += 1
                if count > length:
                    break
                line = lines[ count ]
                parmargs = line.split()
                if parmargs[0] == "Default":
                    tempparm['value'] = _formatVal( ' '.join(parmargs[2:]) )
                elif parmargs[0] == "metadata:":
                    (key, value) = _getKeyValue( line )
                    value = _formatVal( value )
                    if key != 'widget':
                        tempparm[key] = value
                    else:
                        widget.append( value )
                else:
                    condition = False
                    # move one line back
                    count -= 1
            if len(widget) > 0 and 'widget' not in tempparm:
                tempparm['widget'] = widget
            tempShader[tempparm['name']] = tempparm
            parmlist.append(tempparm['name'])
            if 'help' in tempparm:
                tempShader['hasParmHelp'] = True
        # we didn't find a parameter yet, so there must be some general stuff
        else:
            if args[0] == "metadata:":
                (key, value) = _getKeyValue( line )
                value = _formatVal( value )
                tempparm[key] = value
                tempShader['hasMetaData'] = True
  
        if count > length:
           break
        else:
            count += 1
        # parsed all lines
    tempShader['parmlist'] = parmlist
    
    if DEBUG:
        for key in tempShader:
            print( "%s: %s" % ( key, tempShader[key] ) )

    return tempShader
