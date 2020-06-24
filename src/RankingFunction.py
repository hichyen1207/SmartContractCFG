from z3 import *
import src.settings as settings

class RankingFunction:

    def __init__(self, constraints: [BitVecRef], decl: str):
        self.constraints = constraints
        self.decl = decl
        self.if_constraint = list()
        self.cfg_vars = list()
        self.cfg_pvars = list()
        self.cfg_constraint = list()
        self.replace_pattern = list()

    def create_cfg(self):
        for constraint in self.constraints:
            variables = self.get_z3_variable(constraint)
            for variable in variables:
                if str(variable) not in self.cfg_vars:
                    self.cfg_vars.append(str(variable))
                    self.cfg_pvars.append(str(variable)+"'")
        c_prime = str(self.constraints[1])
        for v in self.cfg_vars:
            c_prime = c_prime.replace(v, v+"'")
        c = '%s = %s' % (c_prime, self.constraints[0])
        self.cfg_constraint.append(c)
        if self.decl == 'UGT':
            self.cfg_constraint.append('%s > 0' % self.constraints[0])
        elif self.decl == 'ULT':
            self.cfg_constraint.append('%s < 0' % self.constraints[0])
        else:
            raise Error('Ranking Function Error')
        self.__cfg_format()

    def get_z3_variable(self, constraint: BitVecRef) -> [BitVecRef]:
        variables = list()
        for e in self.__visitor(constraint, {}):
            if is_const(e) and e.decl().kind() == Z3_OP_UNINTERPRETED:
                variables.append(e)
            else:
                if str(e.decl()) == '&':

                if str(e.decl()) == 'If' and e not in self.if_constraint:
                    self.if_constraint.append(e)
        return variables

    def __visitor(self, e, seen):
        if e in seen:
            return
        seen[e] = True
        yield e
        if is_app(e):
            for ch in e.children():
                for e in self.__visitor(ch, seen):
                    yield e
            return
        if is_quantifier(e):
            for e in self.__visitor(e.body(), seen):
                yield e
            return

    def __cfg_format(self):
        self.cfg = '''
{
    vars: [%s],
    pvars: [%s],
    initnode: n0,
    nodes:{},
    transitions: [
        {
            source: n0,
            target: n0,
            name: t0,
            constraints: [%s]
        },
        {
            source: n0,
            target: n1,
            name: t1,
            constraints: [%s]
        },
    ]
}
        ''' % (','.join(self.cfg_vars), ','.join(self.cfg_pvars), ','.join(self.cfg_constraint), ','.join(["%s' = %s" % (x,x) for x in self.cfg_vars]))

    def render(self, name: str) -> None:
        with open('%s/%s/RankingFunciton/%s.fc' % (settings.OUTPUT_PATH, settings.CONTRACT_NAME, name), 'w') as f:
            f.write(self.cfg)