###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import textwrap
import unittest

from slimit.parser import Parser
from slimit import minify

UnitTestMeta = type(unittest.TestCase)


class VisitorTestMeta(UnitTestMeta):
    def __new__(cls, name, bases, attributes):
        try:
            test_cases = attributes['TEST_CASES']
        except KeyError:
            test_cases = [getattr(b, 'TEST_CASES')
                          for b in bases
                          if hasattr(b, 'TEST_CASES')][0]

        def generate_test_func(name, case):
            func = lambda self: self.case(case)
            func.__name__ = name
            return func

        for idx, case in enumerate(test_cases):
            name = 'test_case_{}'.format(idx)
            attributes[name] = generate_test_func(name, case)

        return super(VisitorTestMeta, cls).__new__(cls, name, bases, attributes)


class VisitorTestMixin(object):
    TEST_CASES = [
        ################################
        # block
        ################################
        """
        {
          var a = 5;
        }
        """,

        ################################
        # variable statement
        ################################
        """
        var a;
        var b;
        var a, b = 3;
        var a = 1, b;
        var a = 5, b = 7;
        """,

        # empty statement
        """
        ;
        ;
        ;
        """,

        # test 3
        ################################
        # if
        ################################
        'if (true) var x = 100;',

        """
        if (true) {
          var x = 100;
          var y = 200;
        }
        """,

        'if (true) if (true) var x = 100; else var y = 200;',

        # test 6
        """
        if (true) {
          var x = 100;
        } else {
          var y = 200;
        }
        """,
        ################################
        # iteration
        ################################
        """
        for (i = 0; i < 10; i++) {
          x = 10 * i;
        }
        """,

        """
        for (var i = 0; i < 10; i++) {
          x = 10 * i;
        }
        """,

        # test 9
        """
        for (i = 0, j = 10; i < j && j < 15; i++, j++) {
          x = i * j;
        }
        """,

        """
        for (var i = 0, j = 10; i < j && j < 15; i++, j++) {
          x = i * j;
        }
        """,

        """
        for (p in obj) {

        }
        """,
        # retain the semicolon in the initialiser part of a 'for' statement
        """
        for (Q || (Q = []); d < b; ) {
          d = 1;
        }
        """,

        """
        for (new Foo(); d < b; ) {
          d = 1;
        }
        """,

        """
        for (2 >> (foo ? 32 : 43) && 54; 21; ) {
          a = c;
        }
        """,

        """
        for (/^.+/g; cond(); ++z) {
          ev();
        }
        """,

        # test 12
        """
        for (var p in obj) {
          p = 1;
        }
        """,

        """
        do {
          x += 1;
        } while (true);
        """,

        """
        while (false) {
          x = null;
        }
        """,

        # test 15
        ################################
        # continue statement
        ################################
        """
        while (true) {
          continue;
          s = 'I am not reachable';
        }
        """,

        """
        while (true) {
          continue label1;
          s = 'I am not reachable';
        }
        """,

        ################################
        # break statement
        ################################
        """
        while (true) {
          break;
          s = 'I am not reachable';
        }
        """,
        # test 18
        """
        while (true) {
          break label1;
          s = 'I am not reachable';
        }
        """,

        ################################
        # return statement
        ################################
        """
        {
          return;
        }
        """,

        """
        {
          return 1;
        }
        """,

        # test21
        ################################
        # with statement
        ################################
        """
        with (x) {
          var y = x * 2;
        }
        """,

        ################################
        # labelled statement
        ################################
        """
        label: while (true) {
          x *= 3;
        }
        """,

        ################################
        # switch statement
        ################################
        """
        switch (day_of_week) {
          case 6:
          case 7:
            x = 'Weekend';
            break;
          case 1:
            x = 'Monday';
            break;
          default:
            break;
        }
        """,

        # test 24
        ################################
        # throw statement
        ################################
        """
        throw 'exc';
        """,

        ################################
        # debugger statement
        ################################
        'debugger;',

        ################################
        # expression statement
        ################################
        """
        5 + 7 - 20 * 10;
        ++x;
        --x;
        x++;
        x--;
        x = 17 /= 3;
        s = mot ? z : /x:3;x<5;y</g / i;
        """,

        # test 27
        ################################
        # try statement
        ################################
        """
        try {
          x = 3;
        } catch (exc) {
          x = exc;
        }
        """,

        """
        try {
          x = 3;
        } finally {
          x = null;
        }
        """,

        """
        try {
          x = 5;
        } catch (exc) {
          x = exc;
        } finally {
          y = null;
        }
        """,

        # test 30
        ################################
        # function
        ################################
        """
        function foo(x, y) {
          z = 10;
          return x + y + z;
        }
        """,

        """
        function foo() {
          return 10;
        }
        """,

        """
        var a = function() {
          return 10;
        };
        """,
        # test 33
        """
        var a = function foo(x, y) {
          return x + y;
        };
        """,
        # nested function declaration
        """
        function foo() {
          function bar() {

          }
        }
        """,

        """
        var mult = function(x) {
          return x * 10;
        }();
        """,

        # function call
        # test 36
        'foo();',
        'foo(x, 7);',
        'foo()[10];',
        # test 39
        'foo().foo;',

        ################################
        # misc
        ################################

        # new
        'var foo = new Foo();',
        # dot accessor
        'var bar = new Foo.Bar();',

        # test 42
        # bracket accessor
        'var bar = new Foo.Bar()[7];',

        # object literal
        """
        var obj = {
          foo: 10,
          bar: 20
        };
        """,
        """
        var obj = {
          1: 'a',
          2: 'b'
        };
        """,
        # test 45
        """
        var obj = {
          'a': 100,
          'b': 200
        };
        """,
        """
        var obj = {
        };
        """,

        # array
        """
        var a = [1,2,3,4,5];
        var res = a[3];
        """,
        # test 48
        # elision
        'var a = [,,,];',
        'var a = [1,,,4];',
        'var a = [1,,3,,5];',

        # test 51
        """
        String.prototype.foo = function(data) {
          var tmpl = this.toString();
          return tmpl.replace(/{{\s*(.*?)\s*}}/g, function(a, b) {
            var node = data;
            if (true) {
              var value = true;
            } else {
              var value = false;
            }
            $.each(n.split('.'), function(i, sym) {
              node = node[sym];
            });
            return node;
          });
        };
        """,

        #######################################
        # Make sure parentheses are not removed
        #######################################

        # ... Expected an identifier and instead saw '/'
        'Expr.match[type].source + (/(?![^\[]*\])(?![^\(]*\))/.source);',

        '(options = arguments[i]) != null;',

        # test 54
        'return (/h\d/i).test(elem.nodeName);',

        # https://github.com/rspivak/slimit/issues/42
        """
        e.b(d) ? (a = [c.f(j[1])], e.fn.attr.call(a, d, !0)) : a = [k.f(j[1])];
        """,

        """
        (function() {
          x = 5;
        }());
        """,

        """
        (function() {
          x = 5;
        })();
        """,

        'return !(match === true || elem.getAttribute("classid") !== match);',

        # test 57
        'var el = (elem ? elem.ownerDocument || elem : 0).documentElement;',

        # typeof
        'typeof second.length === "number";',

        # function call in FOR init
        """
        for (o(); i < 3; i++) {

        }
        """,

        # https://github.com/rspivak/slimit/issues/32
        """
        Name.prototype = {
          get fullName() {
            return this.first + " " + this.last;
          },
          set fullName(name) {
            var names = name.split(" ");
            this.first = names[0];
            this.last = names[1];
          }
        };
        """,
        ]


class ECMAVisitorTestCase(VisitorTestMixin, unittest.TestCase):
    __metaclass__ = VisitorTestMeta

    def setUp(self):
        self.maxDiff = 2000

    def case(self, case):
        parser = Parser()
        result = parser.parse(case).to_ecma()
        expected = textwrap.dedent(case).strip()
        self.assertMultiLineEqual(result, expected)


class ParsingTestCase(VisitorTestMixin, unittest.TestCase):
    __metaclass__ = VisitorTestMeta

    def case(self, case):
        parser_a = Parser()
        result_a = parser_a.parse(case)

        parser_b = Parser()
        result_b = parser_b.parse(case)

        self.assertEqual(result_a, result_b)


class MinifierTestCase(unittest.TestCase):
    __metaclass__ = VisitorTestMeta

    def assertMinified(self, source, expected):
        minified = minify(source)
        self.maxDiff = None
        self.assertSequenceEqual(minified, expected)

    def case(self, case):
        input_, expected = case
        self.assertMinified(input_, expected)

    TEST_CASES = [
        ("""
        jQuery.fn = jQuery.prototype = {
                // For internal use only.
                _data: function( elem, name, data ) {
                        return jQuery.data( elem, name, data, true );
                }
        };
        """,
         'jQuery.fn=jQuery.prototype={_data:function(elem,name,data){return jQuery.data(elem,name,data,true);}};'),

        ('context = context instanceof jQuery ? context[0] : context;',
         'context=context instanceof jQuery?context[0]:context;'
         ),

        ("""
        /*
        * A number of helper functions used for managing events.
        * Many of the ideas behind this code originated from
        * Dean Edwards' addEvent library.
        */
        if ( elem && elem.parentNode ) {
                // Handle the case where IE and Opera return items
                // by name instead of ID
                if ( elem.id !== match[2] ) {
                        return rootjQuery.find( selector );
                }

                // Otherwise, we inject the element directly into the jQuery object
                this.length = 1;
                this[0] = elem;
        }
        """,

         'if(elem&&elem.parentNode){if(elem.id!==match[2])return rootjQuery.find(selector);this.length=1;this[0]=elem;}'
         ),

        ("""
        var a = function( obj ) {
                for ( var name in obj ) {
                        return false;
                }
                return true;
        };
        """,
         'var a=function(obj){for(var name in obj)return false;return true;};'
         ),

        ("""
        x = "string", y = 5;

        (x = 5) ? true : false;

        for (p in obj)
        ;

        if (true)
          val = null;
        else
          val = false;

        """,
         'x="string",y=5;(x=5)?true:false;for(p in obj);if(true)val=null;else val=false;'
         ),

        # for loops + empty statement in loop body
        ("""
        for (x = 0; true; x++)
        ;
        for (; true; x++)
        ;
        for (x = 0, y = 5; true; x++)
        ;

        y = (x + 5) * 20;

        """,
         'for(x=0;true;x++);for(;true;x++);for(x=0,y=5;true;x++);y=(x+5)*20;'),


        # unary expressions
        ("""
        delete x;
        typeof x;
        void x;
        x += (!y)++;
        """,
         'delete x;typeof x;void x;x+=(!y)++;'),

        # label + break label + continue label
        ("""
        label:
        if ( i == 0 )
          continue label;
        switch (day) {
        case 5:
          break ;
        default:
          break label;
        }
        """,
         'label:if(i==0)continue label;switch(day){case 5:break;default:break label;}'),

        # break + continue: no labels
        ("""
        while (i <= 7) {
          if ( i == 3 )
              continue;
          if ( i == 0 )
              break;
        }
        """,
         'while(i<=7){if(i==3)continue;if(i==0)break;}'),

        # regex + one line statements in if and if .. else
        ("""
        function a(x, y) {
         var re = /ab+c/;
         if (x == 1)
           return x + y;
         if (x == 3)
           return {x: 1};
         else
           return;
        }
        """,
         'function a(x,y){var re=/ab+c/;if(x==1)return x+y;if(x==3)return{x:1};else return;}'),

        # new
        ('return new jQuery.fn.init( selector, context, rootjQuery );',
         'return new jQuery.fn.init(selector,context,rootjQuery);'
         ),

        # no space after 'else' when the next token is (, {
        ("""
        if (true) {
          x = true;
          y = 3;
        } else {
          x = false
          y = 5
        }
        """,
         'if(true){x=true;y=3;}else{x=false;y=5;}'),

        ("""
        if (true) {
          x = true;
          y = 3;
        } else
          (x + ' qw').split(' ');
        """,
         "if(true){x=true;y=3;}else(x+' qw').split(' ');"),


        ##############################################################
        # Block braces removal
        ##############################################################

        # do while
        ('do { x += 1; } while(true);', 'do x+=1;while(true);'),
        # do while: multiple statements
        ('do { x += 1; y += 1;} while(true);', 'do{x+=1;y+=1;}while(true);'),

        # elision
        ('var a = [1, 2, 3, ,,,5];', 'var a=[1,2,3,,,,5];'),

        # with
        ("""
        with (obj) {
          a = b;
        }
        """,
         'with(obj)a=b;'),

        # with: multiple statements
        ("""
        with (obj) {
          a = b;
          c = d;
        }
        """,
         'with(obj){a=b;c=d;}'),

        # if else
        ("""
        if (true) {
          x = true;
        } else {
          x = false
        }
        """,
         'if(true)x=true;else x=false;'),

        # if: multiple statements
        ("""
        if (true) {
          x = true;
          y = false;
        } else {
          x = false;
          y = true;
        }
        """,
         'if(true){x=true;y=false;}else{x=false;y=true;}'),

        # try catch finally: one statement
        ("""
        try {
          throw "my_exception"; // generates an exception
        }
        catch (e) {
          // statements to handle any exceptions
          log(e); // pass exception object to error handler
        }
        finally {
          closefiles(); // always close the resource
        }
        """,
         'try{throw "my_exception";}catch(e){log(e);}finally{closefiles();}'
         ),

        # try catch finally: no statements
        ("""
        try {
        }
        catch (e) {
        }
        finally {
        }
        """,
         'try{}catch(e){}finally{}'
         ),

        # try catch finally: multiple statements
        ("""
        try {
          x = 3;
          y = 5;
        }
        catch (e) {
          log(e);
          log('e');
        }
        finally {
          z = 7;
          log('z');
        }
        """,
         "try{x=3;y=5;}catch(e){log(e);log('e');}finally{z=7;log('z');}"
         ),

        # tricky case with an 'if' nested in 'if .. else'
        # We need to preserve braces in the first 'if' otherwise
        # 'else' might get associated with nested 'if' instead
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        }
                }
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj){for(n in obj)if(v===false)break;}else for(;i<l;)if(nv===false)break;'),

        # We don't care about nested 'if' when enclosing 'if' block
        # contains multiple statements because braces won't be removed
        # by visit_Block when there are multiple statements in the block
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        }
                }
                x = 5;
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj){for(n in obj)if(v===false)break;x=5;}else for(;i<l;)if(nv===false)break;'),


        # No dangling 'else' - remove braces
        ("""
        if ( obj ) {
                for ( n in obj ) {
                        if ( v === false) {
                                break;
                        } else {
                                n = 3;
                        }
                }
        } else {
                for ( ; i < l; ) {
                        if ( nv === false ) {
                                break;
                        }
                }
        }
        """,
         'if(obj)for(n in obj)if(v===false)break;else n=3;else for(;i<l;)if(nv===false)break;'),

        # foo["bar"] --> foo.bar
        ('foo["bar"];', 'foo.bar;'),
        ("foo['bar'];", 'foo.bar;'),
        ("""foo['bar"']=42;""", """foo['bar"']=42;"""),
        ("""foo["bar'"]=42;""", """foo["bar'"]=42;"""),
        ('foo["bar bar"];', 'foo["bar bar"];'),
        ('foo["bar"+"bar"];', 'foo["bar"+"bar"];'),
        # https://github.com/rspivak/slimit/issues/34
        # test some reserved keywords
        ('foo["for"];', 'foo["for"];'),
        ('foo["class"];', 'foo["class"];'),


        # https://github.com/rspivak/slimit/issues/21
        # c||(c=393,a=323,b=2321); --> c||c=393,a=323,b=2321; ERROR
        ('c||(c=393);', 'c||(c=393);'),
        ('c||(c=393,a=323,b=2321);', 'c||(c=393,a=323,b=2321);'),

        # https://github.com/rspivak/slimit/issues/25
        ('for(a?b:c;d;)e=1;', 'for(a?b:c;d;)e=1;'),

        # https://github.com/rspivak/slimit/issues/26
        ('"begin"+ ++a+"end";', '"begin"+ ++a+"end";'),

        # https://github.com/rspivak/slimit/issues/28
        ("""
         (function($) {
             $.hello = 'world';
         }(jQuery));
         """,
         "(function($){$.hello='world';}(jQuery));"),

        # function call on immediate number
        ('((25)).toString()', '(25).toString();'),
        ('((25))["toString"]()', '(25).toString();'),

        # attribute access on immediate number
        ('((25)).attr', '(25).attr;'),
        ('((25))["attr"]', '(25).attr;'),

        # function call in FOR init
        ('for(o(); i < 3; i++) {}', 'for(o();i<3;i++){}'),

        # unary increment operator in FOR init
        ('for(i++; i < 3; i++) {}', 'for(i++;i<3;i++){}'),

        # unary decrement operator in FOR init
        ('for(i--; i < 3; i++) {}', 'for(i--;i<3;i++){}'),

        # issue-37, simple identifier in FOR init
        ('for(i; i < 3; i++) {}', 'for(i;i<3;i++){}'),

        # https://github.com/rspivak/slimit/issues/32
        ("""
         Name.prototype = {
           getPageProp: function Page_getPageProp(key) {
             return this.pageDict.get(key);
           },

           get fullName() {
             return this.first + " " + this.last;
           },

           set fullName(name) {
             var names = name.split(" ");
             this.first = names[0];
             this.last = names[1];
           }
         };
         """,
         ('Name.prototype={getPageProp:function Page_getPageProp(key){'
          'return this.pageDict.get(key);},'
          'get fullName(){return this.first+" "+this.last;},'
          'set fullName(name){var names=name.split(" ");this.first=names[0];'
          'this.last=names[1];}};')
        ),

        # https://github.com/rspivak/slimit/issues/47 - might be a Python 3
        # related issue
        ('testObj[":"] = undefined; // Breaks', 'testObj[":"]=undefined;'),
        ('testObj["::"] = undefined; // Breaks', 'testObj["::"]=undefined;'),
        ('testObj["a:"] = undefined; // Breaks', 'testObj["a:"]=undefined;'),
        ('testObj["."] = undefined; // OK', 'testObj["."]=undefined;'),
        ('testObj["{"] = undefined; // OK', 'testObj["{"]=undefined;'),
        ('testObj["}"] = undefined; // OK', 'testObj["}"]=undefined;'),
        ('testObj["["] = undefined; // Breaks', 'testObj["["]=undefined;'),
        ('testObj["]"] = undefined; // Breaks', 'testObj["]"]=undefined;'),
        ('testObj["("] = undefined; // OK', 'testObj["("]=undefined;'),
        ('testObj[")"] = undefined; // OK', 'testObj[")"]=undefined;'),
        ('testObj["="] = undefined; // Breaks', 'testObj["="]=undefined;'),
        ('testObj["-"] = undefined; // OK', 'testObj["-"]=undefined;'),
        ('testObj["+"] = undefined; // OK', 'testObj["+"]=undefined;'),
        ('testObj["*"] = undefined; // OK', 'testObj["*"]=undefined;'),
        ('testObj["/"] = undefined; // OK', 'testObj["/"]=undefined;'),
        (r'testObj["\\"] = undefined; // Breaks', r'testObj["\\"]=undefined;'),
        ('testObj["%"] = undefined; // OK', 'testObj["%"]=undefined;'),
        ('testObj["<"] = undefined; // Breaks', 'testObj["<"]=undefined;'),
        ('testObj[">"] = undefined; // Breaks', 'testObj[">"]=undefined;'),
        ('testObj["!"] = undefined; // OK', 'testObj["!"]=undefined;'),
        ('testObj["?"] = undefined; // Breaks', 'testObj["?"]=undefined;'),
        ('testObj[","] = undefined; // OK', 'testObj[","]=undefined;'),
        ('testObj["@"] = undefined; // Breaks', 'testObj["@"]=undefined;'),
        ('testObj["#"] = undefined; // OK', 'testObj["#"]=undefined;'),
        ('testObj["&"] = undefined; // OK', 'testObj["&"]=undefined;'),
        ('testObj["|"] = undefined; // OK', 'testObj["|"]=undefined;'),
        ('testObj["~"] = undefined; // OK', 'testObj["~"]=undefined;'),
        ('testObj["`"] = undefined; // Breaks', 'testObj["`"]=undefined;'),
        ('testObj["."] = undefined; // OK', 'testObj["."]=undefined;'),
        ]


class MinifierReparsingTestCase(unittest.TestCase):
    __metaclass__ = VisitorTestMeta

    TEST_CASES = [
        """
        a + +a;
        """,

        """
        a - -a;
        """,

        """
        a - +a;
        """,

        """
        a + ++a;
        """,

        """
        a - --a;
        """
    ]

    def case(self, case):
        parsed = Parser().parse(case)
        minified = Parser().parse(minify(case))
        self.assertEqual(parsed, minified)
