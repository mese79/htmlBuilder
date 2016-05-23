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


class Node(object):
    def __init__(self, children=None, p=None):
        self._children_list = [] if children is None else children
        self.setpos(p)

    def setpos(self, p):
        self.lexpos = None if p is None else p.lexpos(1);
        self.lineno = None if p is None else p.lineno(1);
        # print 'setpos', self, p, self.lexpos, self.lineno

    def __iter__(self):
        for child in self.children():
            if child is not None:
                yield child

    def children(self):
        return self._children_list

    def to_ecma(self):
        # Can't import at module level as ecmavisitor depends
        # on ast module...
        from slimit.visitors.ecmavisitor import ECMAVisitor
        visitor = ECMAVisitor()
        return visitor.visit(self)

    def _eq(self, other):
        if len(self.children()) != len(other.children()):
            return False
        else:
            l = zip(self.children(), other.children())
            return all(s == o for s, o in l)

    def __eq__(self, other):
        if type(self) == type(other):
            return self._eq(other)
        elif isinstance(other, Node):
            return False
        else:
            return NotImplemented

class Program(Node):
    def __repr__(self):
        return 'Program(children={!r})'.format(self.children())

class Block(Node):
    def __repr__(self):
        return 'Block(children={!r})'.format(self.children())

class Boolean(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return self.value == other.value

    def __repr__(self):
        return 'Boolean({!r})'.format(self.value)

class Null(Node):
    def __init__(self, value):
        assert value == 'null'
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return True  # A null value is always equal to another null value

    def __repr__(self):
        return 'Null()'

class Number(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return self.value == other.value

    def __repr__(self):
        return 'Number(value={!r})'.format(self.value)

class Identifier(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return self.value == other.value

    def __repr__(self):
        return 'Identifier(value={!r})'.format(self.value)

class String(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return self.value == other.value

    def __repr__(self):
        return 'String(value={!r})'.format(self.value)

class Regex(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return self.value == other.value

    def __repr__(self):
        return 'Regex(value={!r})'.format(self.value)

class Array(Node):
    def __init__(self, items):
        self.items = items

    def children(self):
        return self.items

    def __repr__(self):
        return 'Array(items={!r})'.format(self.items)

    def _eq(self, other):
        return self.items == other.items

class Object(Node):
    def __init__(self, properties=None):
        self.properties = [] if properties is None else properties

    def children(self):
        return self.properties

    def _eq(self, other):
        return self.properties == other.properties

    def __repr__(self):
        return 'Object(properties={!r})'.format(self.properties)

class NewExpr(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier, self.args]

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.args == other.args)
        )

    def __repr__(self):
        return 'NewExpr(identifier={!r}, args={!r})'.format(
            self.identifier, self.args)

class FunctionCall(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier] + self.args

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.args == other.args)
        )

    def __repr__(self):
        return 'FunctionCall(identifier={!r}, args={!r})'.format(
            self.identifier, self.args)

class BracketAccessor(Node):
    def __init__(self, node, expr):
        self.node = node
        self.expr = expr

    def children(self):
        return [self.node, self.expr]

    def _eq(self, other):
        return (
            (self.node == other.node) and
            (self.expr == other.expr)
        )

    def __repr__(self):
        return 'BracketAccessor(node={!r}, expr={!r})'.format(
            self.node, self.expr)

class DotAccessor(Node):
    def __init__(self, node, identifier):
        self.node = node
        self.identifier = identifier

    def children(self):
        return [self.node, self.identifier]

    def _eq(self, other):
        return (
            (self.node == other.node) and
            (self.identifier == other.identifier)
        )

    def __repr__(self):
        return 'DotAccessor(node={!r}, identifier={!r})'.format(
            self.node, self.identifier)

class Assign(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

    def _eq(self, other):
        return (
            (self.op == other.op) and
            (self.left == other.left) and
            (self.right == other.right)
        )

    def __repr__(self):
        return 'Assign(op={!r}, left={!r}, right={!r})'.format(
            self.op, self.left, self.right)

class GetPropAssign(Node):
    def __init__(self, prop_name, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.elements

    def _eq(self, other):
        return (
            (self.prop_name == other.prop_name) and
            (self.elements == other.elements)
        )

    def __repr__(self):
        return 'GetPropAssign(prop_name={!r}, elements={!r})'.format(
            self.prop_name, self.elements)

class SetPropAssign(Node):
    def __init__(self, prop_name, parameters, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.parameters = parameters
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.parameters + self.elements

    def _eq(self, other):
        return (
            (self.prop_name == other.prop_name) and
            (self.parameters == other.parameters) and
            (self.elements == other.elements)
        )

    def __repr__(self):
        fmt = 'SetPropAssign(prop_name={!r}, parameters={!r}, elements={!r}'
        return fmt.format(self.prop_name, self.parameters, self.elements)

class VarStatement(Node):
    def __repr__(self):
        return 'VarStatement(children={!r})'.format(self.children())

class VarDecl(Node):
    def __init__(self, identifier, initializer=None, p=None):
        self.identifier = identifier
        self.identifier._mangle_candidate = True
        self.initializer = initializer
        self.setpos(p)

    def children(self):
        return [self.identifier, self.initializer]

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.initializer == other.initializer)
        )

    def __repr__(self):
        return 'VarDecl(identifier={!r}, initializer={!r})'.format(
            self.identifier, self.initializer)

class UnaryOp(Node):
    def __init__(self, op, value, postfix=False):
        self.op = op
        self.value = value
        self.postfix = postfix

    def children(self):
        return [self.value]

    def _eq(self, other):
        return (
            (self.op == other.op) and
            (self.value == other.value) and
            (self.postfix == other.postfix)
        )

    def __repr__(self):
        return 'UnaryOp(op={!r}, value={!r}, postfix={!r})'.format(
            self.op, self.value, self.postfix)

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

    def _eq(self, other):
        return (
            (self.op == other.op) and
            (self.left == other.left) and
            (self.right == other.right)
        )

    def __repr__(self):
        return 'BinOp(op={!r}, left={!r}, right={!r})'.format(
            self.op, self.left, self.right)

class Conditional(Node):
    """Conditional Operator ( ? : )"""
    def __init__(self, predicate, consequent, alternative):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

    def _eq(self, other):
        return (
            (self.predicate == other.predicate) and
            (self.consequent == other.consequent) and
            (self.alternative == other.alternative)
        )

    def __repr__(self):
        fmt = 'Conditional(predicate={!r}, consequent={!r}, alternative={!r})'
        return fmt.format(self.predicate, self.consequent, self.alternative)

class If(Node):
    def __init__(self, predicate, consequent, alternative=None):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

    def _eq(self, other):
        return (
            (self.predicate == other.predicate) and
            (self.consequent == other.consequent) and
            (self.alternative == other.alternative)
        )

    def __repr__(self):
        return 'If(predicate={!r}, consequent={!r}, alternative={!r})'.format(
            self.predicate, self.consequent, self.alternative)

class DoWhile(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

    def _eq(self, other):
        return (
            (self.predicate == other.predicate) and
            (self.statement == other.statement)
        )

    def __repr__(self):
        return 'DoWhile(predicate={!r}, statement={!r})'.format(
            self.predicate, self.statement)

class While(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

    def _eq(self, other):
        return (
            (self.predicate == other.predicate) and
            (self.statement == other.statement)
        )

    def __repr__(self):
        return 'While(predicate={!r}, statement={!r})'.format(
            self.predicate, self.statement)

class For(Node):
    def __init__(self, init, cond, count, statement):
        self.init = init
        self.cond = cond
        self.count = count
        self.statement = statement

    def children(self):
        return [self.init, self.cond, self.count, self.statement]

    def _eq(self, other):
        return (
            (self.init == other.init) and
            (self.cond == other.cond) and
            (self.count == other.count) and
            (self.statement == other.statement)
        )

    def __repr__(self):
        return 'For(init={!r}, cond={!r}, count={!r}, statement={!r})'.format(
            self.init, self.cond, self.count, self.statement)

class ForIn(Node):
    def __init__(self, item, iterable, statement):
        self.item = item
        self.iterable = iterable
        self.statement = statement

    def children(self):
        return [self.item, self.iterable, self.statement]

    def _eq(self, other):
        return (
            (self.item == other.item) and
            (self.iterable == other.iterable) and
            (self.statement == other.statement)
        )

    def __repr__(self):
        return 'ForIn(item={!r}, iterable={!r}, statement={!r})'.format(
            self.item, self.iterable, self.statement)

class Continue(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

    def _eq(self, other):
        return True  # A continue statement is always the same as another one

    def __repr__(self):
        return 'Continue()'

class Break(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

    def _eq(self, other):
        return True  # A break statement is always the same as another one

    def __repr__(self):
        return 'Break()'

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr

    def children(self):
        return [self.expr]

    def _eq(self, other):
        return self.expr == other.expr

    def __repr__(self):
        return 'Return(expr={!r})'.format(self.expr)

class With(Node):
    def __init__(self, expr, statement):
        self.expr = expr
        self.statement = statement

    def children(self):
        return [self.expr, self.statement]

    def _eq(self, other):
        return self.expr == other.expr

    def __repr__(self):
        return 'With(expr={!r})'.format(self.expr)

class Switch(Node):
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases
        self.default = default

    def children(self):
        return [self.expr] + self.cases + [self.default]

    def _eq(self, other):
        return (
            (self.expr == other.expr) and
            (self.cases == other.cases) and
            (self.default == other.default)
        )

    def __repr__(self):
        return 'Switch(expr={!r}, cases={!r}, default={!r})'.format(
            self.expr, self.cases, self.default)

class Case(Node):
    def __init__(self, expr, elements):
        self.expr = expr
        self.elements = elements if elements is not None else []

    def children(self):
        return [self.expr] + self.elements

    def _eq(self, other):
        return (
            (self.expr == other.expr) and
            (self.elements == other.elements)
        )

    def __repr__(self):
        return 'Case(expr={!r}, elements={!r})'.format(
            self.expr, self.elements)

class Default(Node):
    def __init__(self, elements):
        self.elements = elements if elements is not None else []

    def children(self):
        return self.elements

    def _eq(self, other):
        return self.elements == other.elements

    def __repr__(self):
        return 'Default(elements={!r})'.format(self.elements)

class Label(Node):
    def __init__(self, identifier, statement):
        self.identifier = identifier
        self.statement = statement

    def children(self):
        return [self.identifier, self.statement]

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.statement == other.statement)
        )

    def __repr__(self):
        return 'Label(identifier={!r}, statement={!r})'.format(
            self.identifier, self.statement)

class Throw(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

    def _eq(self, other):
        return self.expr == other.expr

    def __repr__(self):
        return 'Throw(expr={!r})'.format(self.expr)

class Try(Node):
    def __init__(self, statements, catch=None, fin=None):
        self.statements = statements
        self.catch = catch
        self.fin = fin

    def children(self):
        return [self.statements] + [self.catch, self.fin]

    def _eq(self, other):
        return (
            (self.statements == other.statements) and
            (self.catch == other.catch) and
            (self.fin == other.fin)
        )

    def __repr__(self):
        return 'Try(statement={!r}, catch={!r}, fin={!r})'.format(
            self.statement, self.catch, self.fin)

class Catch(Node):
    def __init__(self, identifier, elements):
        self.identifier = identifier
        # CATCH identifiers are subject to name mangling. we need to mark them.
        self.identifier._mangle_candidate = True
        self.elements = elements

    def children(self):
        return [self.identifier, self.elements]

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.elements == other.elements)
        )

    def __repr__(self):
        return 'Catch(identifier={!r}, elements={!r})'.format(
            self.identifier, self.elements)

class Finally(Node):
    def __init__(self, elements):
        self.elements = elements

    def children(self):
        return self.elements

    def _eq(self, other):
        return self.elements == other.elements

    def __repr__(self):
        return 'Finally(elements={!r})'.format(self.elements)

class Debugger(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return True  # Two debugger statements are equal

    def __repr__(self):
        return 'Debugger()'


class FuncBase(Node):
    def __init__(self, identifier, parameters, elements):
        self.identifier = identifier
        self.parameters = parameters if parameters is not None else []
        self.elements = elements if elements is not None else []
        self._init_ids()

    def _init_ids(self):
        # function declaration/expression name and parameters are identifiers
        # and therefore are subject to name mangling. we need to mark them.
        if self.identifier is not None:
            self.identifier._mangle_candidate = True
        for param in self.parameters:
            param._mangle_candidate = True

    def children(self):
        return [self.identifier] + self.parameters + self.elements

    def _eq(self, other):
        return (
            (self.identifier == other.identifier) and
            (self.parameters == other.parameters) and
            (self.elements == other.elements)
        )

    def __repr__(self):
        # Could be FuncDecl, FuncExpr
        name = type(self).__name__
        fmt = name + '(identifier={!r}, parameters={!r}, elements={!r})'
        return fmt.format(self.identifier, self.parameters, self.elements)

class FuncDecl(FuncBase):
    pass

# The only difference is that function expression might not have an identifier
class FuncExpr(FuncBase):
    pass


class Comma(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

    def _eq(self, other):
        return (
            (self.left == other.left) and
            (self.right == other.right)
        )

    def __repr__(self):
        return 'Comma(left={!r}, right={!r})'.format(self.left, self.right)

class EmptyStatement(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return True  # Two empty statements are equal

    def __repr__(self):
        return 'EmptyStatement()'

class ExprStatement(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

    def _eq(self, other):
        return self.expr == other.expr

    def __repr__(self):
        return 'ExprStatement(expr={!r})'.format(self.expr)

class Elision(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

    def _eq(self, other):
        return True  # Two elisions are equal

    def __repr__(self):
        return 'Elision()'

class This(Node):
    def __init__(self):
        pass

    def children(self):
        return []

    def _eq(self, other):
        return True  # Two this objects are always equal

    def __repr__(self):
        return 'This()'
