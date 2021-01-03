"""
Note: "termination" is the term used in antelope software to describe the process of connecting foreground
nodes to either background processes or environmental contexts.
"""
from .kw_dict import mk_kwd
from antelope import MultipleReferences


class NoTermFound(Exception):
    """
    Used when a flow's properties do not show up in the term dict
    """
    pass


class NoTermEntry(Exception):
    """
    Used when a particular origin is not found in a term dict entry
    """
    pass


class PsmTerminationBuilder(object):
    """
    A tool to build container fragments for product system models, themselves modeled as fragments.

    Uses data in a "terminations" XLS sheet to map flows to terminations based on properties of the flow.  The flow
    properties are used as key headers in the kw_dict; the origins are the column headers used as keys in the lookup
    dicts.

    Other than the keyword dictionary, the functionality of this class is mainly to handle/manipulate fragments using
    the catalog and foreground interface.
    """
    def __init__(self, cat, fg, term_info, sheet='targets'):
        self.cat = cat
        self.fg = fg
        self.term_dict = mk_kwd(term_info, sheet, kwcols=2, lower=False)

    def _get_term_dict(self, flow):
        key = tuple((flow.get(k) or '').strip() for k in self.term_dict[None])
        try:
            return self.term_dict[key]
        except KeyError:
            print(flow)
            raise NoTermFound(key)

    def _get_term_from_dict(self, td, key):
        if key not in td or td[key] is None:
            raise NoTermEntry
        try:
            proc = self.cat.query(key).get(td[key])
        except KeyError:
            print('origin: %s | unable to retrieve %s' % (key, td[key]))
            raise NoTermEntry
        return proc

    def terminate_by_dict(self, leaf, *origins):
        _td = self._get_term_dict(leaf.flow)

        if len(origins) == 0:
            origins = list(_td.keys())

        for k in origins:
            try:
                proc = self._get_term_from_dict(_td, k)
            except NoTermEntry:
                continue
            try:
                rx = proc.reference()
            except MultipleReferences:
                # for this it doesn't matter-- in production we would need to specify a reference flow as well as process
                rx = next(proc.references())
            leaf.terminate(proc, scenario=k, term_flow=rx.flow)

    def terminate_leaf_nodes(self, frag, origin, scenario=None, background=True):
        """
        Given a fragment, traverses the fragment according to the named scenario and terminates every null fragment
        encountered according to the term dict, using the specified origin.
        :param frag:
        :param origin:
        :param scenario:
        :param background: [True] whether to terminate to a background process or a foreground process
        :return:
        """
        ffs = frag.traverse(scenario)
        for ff in ffs:
            if not ff.term.is_null:
                continue
            if not hasattr(ff.fragment, 'set_background'):
                continue  # ghost fragment-- aggregation result
            print(ff)
            _td = self._get_term_dict(ff.fragment.flow)
            try:
                proc = self._get_term_from_dict(_td, origin)
            except NoTermEntry:
                continue
            try:
                rx = proc.reference()
            except MultipleReferences:
                # for this it doesn't matter-- in production we would need to specify a reference flow as well as process
                rx = next(proc.references())
            if background:
                ff.fragment.set_background()
            ff.fragment.terminate(proc, scenario=scenario, term_flow=rx.flow)

    def build_container(self, psm, *origins, descend=True):
        container = self.fg.new_fragment(psm.flow, 'Output', Comment='Container for %s' % psm.name)
        self.fg.observe(container, name='%s Container' % psm.flow.name)
        container.terminate(psm, descend=descend)

        # should be an interface for this- child flows
        for c in psm.inventory():
            if c.is_reference:
                continue
            # if container_frag.has_child(c.flow, c.direction):
            #    continue
            _f = self.fg.new_fragment(c.flow, c.direction, parent=container)
            _f.set_background()

        for f in container.child_flows:
            self.terminate_by_dict(f, *origins)

        return container
