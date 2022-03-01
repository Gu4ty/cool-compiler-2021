from compiler.cmp.grammar import G
from compiler.lexer.lex import CoolLexer
from compiler.parser.parser import LR1Parser, evaluate_reverse_parse
from compiler.visitors.cil_formatter import PrintCILVisitor
from compiler.visitors.cool2cil import COOLToCILVisitor
from compiler.visitors.formatter import FormatVisitor
from compiler.visitors.type_collector import TypeCollector
from compiler.visitors.type_builder import TypeBuilder
from compiler.visitors.type_checker import TypeChecker
from compiler.visitors.type_inferencer import TypeInferencer
from sys import exit

# from compiler.visitors.cool2cil import COOLToCILVisitor
from compiler.visitors.cool2cil import COOLToCILVisitor
from compiler.visitors.cil_formatter import PrintCILVisitor
from compiler.visitors.cil2mips import CILToMIPSVisitor
from compiler.visitors.mips_printer import MIPSPrintVisitor


def main(args):
    try:
        with open(args.file, "r") as fd:
            code = fd.read()
    except:
        print(f"(0,0) - CompilerError: file {args.file} not found")
        exit(1)

    # Lexer
    lexer = CoolLexer()
    tokens, errors = lexer.tokenize(code)
    for error in errors:
        print(error)
    if errors:
        exit(1)

    # Parser
    parser = LR1Parser(G)
    parseResult, error = parser(tokens, get_shift_reduce=True)
    if error:
        print(error)
        exit(1)

    parse, operations = parseResult
    ast = evaluate_reverse_parse(parse, operations, tokens)

    # Collecting types
    collector = TypeCollector()
    collector.visit(ast)
    context = collector.context
    for (e, pos) in collector.errors:
        print(f"{pos} - {type(e).__name__}: {str(e)}")
    if collector.errors:
        exit(1)

    # Building types
    builder = TypeBuilder(context)
    builder.visit(ast)
    manager = builder.manager
    for (e, pos) in builder.errors:
        print(f"{pos} - {type(e).__name__}: {str(e)}")
    if builder.errors:
        exit(1)

    # Type checking
    checker = TypeChecker(context, manager)
    scope = checker.visit(ast)
    for (e, pos) in checker.errors:
        print(f"{pos} - {type(e).__name__}: {str(e)}")
    if checker.errors:
        exit(1)

    # # Inferencing Autotype
    # inferencer = TypeInferencer(context, manager)
    # inferencer.visit(ast, scope)
    # for e in inferencer.errors:
    #     print(f"{pos} - {type(e).__name__}: {str(e)}")
    # if inferencer.errors:
    #     exit(1)

    # # Last check without autotypes
    # checker = TypeChecker(context, manager)
    # checker.visit(ast)
    # for (e, pos) in checker.errors:
    #     print(f"{pos} - {type(e).__name__}: {str(e)}")
    # if checker.errors:
    #     exit(1)

    # COOL to CIL
    cil_visitor = COOLToCILVisitor(context)
    cil_ast = cil_visitor.visit(ast, scope)

    print("*****************************CIL CODE **************************")
    cil_formatter = PrintCILVisitor()
    print(cil_formatter.visit(cil_ast))
    print("*****************************CIL CODE **************************")

    cil_to_mips = CILToMIPSVisitor()
    mips_ast = cil_to_mips.visit(cil_ast)
    printer = MIPSPrintVisitor()
    mips_code = printer.visit(mips_ast)
    # print(mips_code)

    out_file = args.file.split(".")
    out_file[-1] = "mips"
    out_file = ".".join(out_file)
    out_file = f"{args.file[:-3]}.mips"

    with open(out_file, "w") as f:
        f.write(mips_code)
        with open("src/compiler/visitors/mips_lib.asm") as f2:
            f.write("".join(f2.readlines()))

    exit(0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CoolCompiler")
    parser.add_argument(
        "-f", "--file", type=str, default="code.cl", help="File to read cool code from"
    )

    args = parser.parse_args()

    main(args)
