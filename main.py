# -*- coding: UTF-8 -*-
import opcodes_cfg_builder
import symbolic_simulation
import argparse
import os
import global_vars
import result_file
import graph
import attack_synthesis
import preprocessing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sourcecode', help='input source code file', action='store_true')
    parser.add_argument('-b', '--bytecode', help='input bytecode file', action='store_true')
    parser.add_argument('-code', '--code', help='source code')
    parser.add_argument('-gas', '--gas', help='gas limit')

    args = parser.parse_args()

    if args.sourcecode:
        if args.code == '' or args.gas == '':
            print('Error')
            exit(0)
        else:
            f_src = os.path.join(os.path.dirname(__file__), args.code)
            contract_name = os.path.basename(f_src).split('.')[0]

            global_vars.set_gas_limit(int(args.gas))

            print('[INFO] Start Transforming contract %s source code to opcodes.' % contract_name)
            # NOTE: Compile source code to opcodes
            preprocessing.source_code_to_opcodes(f_src)

            # NOTE: Analyze the opcodes
            opcodes_analysis(contract_name)
    elif args.bytecode:
        if args.code == '' or args.gas == '':
            print('Error')
            exit(0)
        else:
            f_src = os.path.join(os.path.dirname(__file__), args.code)
            contract_name = os.path.basename(f_src).split('.')[0]

            global_vars.set_gas_limit(int(args.gas))

            print('[INFO] Start Transforming contract %s source code to opcodes.' % contract_name)
            # NOTE: Compile source code to opcodes
            preprocessing.bytecode_to_opcodes(f_src)

            # NOTE: Analyze the opcodes
            opcodes_analysis(contract_name)
    else:
        print('Must use an argument, -s for individual source code')


def opcodes_analysis(contract_name):
    for file in os.listdir('./opcodes/%s' % contract_name):
        file_name = file.split('.')[0]
        with open('./opcodes/%s/%s' % (contract_name, file), 'r') as f:
            opcodes = f.read()

        if opcodes != '':
            global_vars.init()
            nodes, edges = opcodes_cfg_builder.cfg_construction(opcodes, file_name)
            graph.create_graph(nodes, edges, contract_name, file_name)

            nodes_size, edges_size, ins_size = graph.graph_detail(nodes, edges)
            print('[INFO] CFG node count = ', nodes_size)
            print('[INFO] CFG edge count = ', edges_size)
            print('[INFO] Total instructions: ', ins_size, '\n')

            nodes, edges = symbolic_simulation.symbolic_simulation(nodes, edges)
            graph.create_graph(nodes, edges, contract_name, file_name)
            max_gas = conformation(nodes)
            result_file.output_result(contract_name, file_name, nodes_size, edges_size, ins_size, max_gas)


def conformation(nodes):
    global_vars.init_generator()
    paths = global_vars.get_pc_gas()
    gas_list = list()
    for path in paths:
        model = path['ans']
        tags = path['path']
        gas = attack_synthesis.attack_synthesis(tags, nodes, model)
        path['real gas'] = gas
        gas_list.append(gas)
    if gas_list:
        return max(gas_list)
    else:
        return 0


if __name__ == '__main__':
    main()
