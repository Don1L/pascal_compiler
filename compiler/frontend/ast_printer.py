import os
import sys
from typing import TextIO, Sequence

from compiler.analysis import visitor
from compiler.frontend.ast import *


class AstPrinter:
    """Печатает AST-дерево в виде дерева с отступами (├ └ │)."""

    @visitor.on('node')
    def view(self, node):
        pass

    @visitor.when(AstNode)
    def view(self, node: AstNode) -> tuple[str, Sequence[AstNode]]:
        return str(node), node.children

    @visitor.when(LiteralNode)
    def view(self, node: LiteralNode) -> tuple[str, Sequence]:
        return node.literal, ()

    @visitor.when(IdentNode)
    def view(self, node: IdentNode) -> tuple[str, Sequence]:
        return node.name, ()

    @visitor.when(TypeNode)
    def view(self, node: TypeNode) -> tuple[str, Sequence]:
        return str(node), ()

    @visitor.when(AssignNode)
    def view(self, node: AssignNode) -> tuple[str, Sequence]:
        return ':=', (node.var, node.value)

    @visitor.when(VarDeclNode)
    def view(self, node: VarDeclNode) -> tuple[str, Sequence]:
        return f'var: {node.type}', node.vars

    @visitor.when(ParamNode)
    def view(self, node: ParamNode) -> tuple[str, Sequence]:
        return f'param {node.name}: {node.type}', ()

    @visitor.when(CallNode)
    def view(self, node: CallNode) -> tuple[str, Sequence]:
        return f'{node.name}()', node.params

    @visitor.when(IfNode)
    def view(self, node: IfNode) -> tuple[str, Sequence]:
        children = [node.cond, node.then_stmt]
        if node.else_stmt:
            children.append(node.else_stmt)
        return 'if', children

    @visitor.when(WhileNode)
    def view(self, node: WhileNode) -> tuple[str, Sequence]:
        return 'while', (node.cond, node.body)

    @visitor.when(ForNode)
    def view(self, node: ForNode) -> tuple[str, Sequence]:
        direction = 'downto' if node.downto else 'to'
        return f'for {node.var} := ... {direction} ...', (node.start, node.finish, node.body)

    @visitor.when(RepeatNode)
    def view(self, node: RepeatNode) -> tuple[str, Sequence]:
        return 'repeat', (*node.body.stmts, node.cond)

    @visitor.when(BinOpNode)
    def view(self, node: BinOpNode) -> tuple[str, Sequence]:
        return str(node.op), (node.arg1, node.arg2)

    @visitor.when(UnOpNode)
    def view(self, node: UnOpNode) -> tuple[str, Sequence]:
        return str(node.op), (node.arg,)

    @visitor.when(StmtListNode)
    def view(self, node: StmtListNode) -> tuple[str, Sequence]:
        return '...', node.stmts

    @visitor.when(ProgramNode)
    def view(self, node: ProgramNode) -> tuple[str, Sequence]:
        children = list(node.var_decls) + list(node.func_decls) + [node.body]
        return str(node), children

    @visitor.when(FuncNode)
    def view(self, node: FuncNode) -> tuple[str, Sequence]:
        children = list(node.params) + list(node.var_decls) + [node.body]
        return str(node), children

    @visitor.when(ForNode)
    def view(self, node: ForNode) -> tuple[str, Sequence]:
        direction = 'downto' if node.downto else 'to'
        return f'for {node.var} := ... {direction} ...', (node.start, node.finish, node.body)

    @visitor.when(TypeConvertNode)
    def view(self, node: TypeConvertNode) -> tuple[str, Sequence]:
        return f'convert({node.type})', (node.value,)

    def _tree_lines(self, node: AstNode) -> list[str]:
        result = self.view(node)
        if isinstance(result, tuple):
            label, children = result
        else:
            label, children = result, node.children

        # Добавляем семантическую аннотацию
        sem = ''
        if node.node_ident:
            sem = f' : {node.node_ident}'
        elif node.node_type:
            sem = f' : {node.node_type}'
        label = str(label) + sem

        lines = [label]
        children = list(children)
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            prefix0 = '└ ' if is_last else '├ '
            prefixN = '  ' if is_last else '│ '
            for j, line in enumerate(self._tree_lines(child)):
                lines.append((prefix0 if j == 0 else prefixN) + line)
        return lines

    def print_tree(self, node: AstNode, file: TextIO = None) -> None:
        out = file or sys.stdout
        print(os.linesep.join(self._tree_lines(node)), file=out)

    @visitor.when(BreakNode)
    def view(self, node: BreakNode) -> tuple[str, tuple]:
        return 'break', ()

    @visitor.when(ContinueNode)
    def view(self, node: ContinueNode) -> tuple[str, tuple]:
        return 'continue', ()

    @visitor.when(ReturnNode)
    def view(self, node: ReturnNode) -> tuple[str, tuple]:
        children = (node.value,) if node.value else ()
        return 'return', children

    @staticmethod
    def print(node: AstNode, file: TextIO = None) -> None:
        AstPrinter().print_tree(node, file)
