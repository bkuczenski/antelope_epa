from antelope_epa.tests.config import ANNOTATED_XLSX_REL_PATH, TRUE_FG_NAME, catalog_dir
from antelope_foreground import ForegroundCatalog

from antelope_epa  import create_epa_psms, mock_inventory_data, create_annotated_foreground
from antelope_epa.terminations import PsmTerminationBuilder
from antelope_epa.exceptions import NotConfiguredError, MissingEpaForegroundEnvVar

from lca_disclosures.antelope import AntelopeTraversalDisclosure

import os


OUTPUT_DIR = 'anon-output'
small = 'ANON_777789 ASSEMBLY'
large = 'ANON_966501 ASSEMBLY'


def simple_product_model_disclosures(cat, fg_name, termination_file, psm=small, quiet=True,
                                     folder=OUTPUT_DIR):
    """
    Creates a set of disclosures describing the simplest product model, 74A400800-1001 Retract Actuator assembly.
    Demonstrates the use of the PsmTerminationBuilder class to build a container fragment (whose child flows are
    populated by cutoffs from interior subfragments), and to terminate cutoff fragments by scenario.

    The disclosure is generated from a traversal of a fragment according to a scenario (or set of scenarios).  One
    key parameter in the traversal is whether to "descend" into sub-fragments, treating them as part of the parent
    fragment, or to treat them as distinct fragments ("non-descend").  The non-descend option reveals some additional
    information, because the linkages between the subfragment and the parent must be made explicit in the disclosure.

    This function creates four disclosures of the same product model:
     - container fragment terminated to USLCI, descend
     - container fragment terminated to USEEIO, descend
     - container fragment terminated to USLCI, non-descend
     - leaf nodes terminated to USLCI (descend is not relevant because container fragment doesn't do anything)

    :param cat:
    :param fg_name:
    :param termination_file:
    :param psm:
    :param quiet:
    :param folder:
    :return:
    """

    fg = cat.foreground(fg_name, reset=True)
    simple_frag = fg.get(psm)

    builder = PsmTerminationBuilder(cat, fg, termination_file, sheet='terminations')

    builder.terminate_leaf_nodes(simple_frag, 'local.uslci.olca', scenario='breakout uslci')

    container_frag = builder.build_container(simple_frag, 'local.uslci.olca', 'local.usepa.useeio.1.1')

    print('Generating Disclosures for simple product model:\n%s\n' % simple_frag)

    print('Descend into subfragments; USLCI termination')
    d = AntelopeTraversalDisclosure(container_frag.traverse('local.uslci.olca'), quiet=quiet, folder_path=folder)
    d.write_excel('simple_uslci_descend')

    print('Descend into subfragments; USEEIO termination')
    d = AntelopeTraversalDisclosure(container_frag.traverse('local.usepa.useeio.1.1'), quiet=quiet, folder_path=folder)
    d.write_excel('simple_useeio_descend')

    print('Non-Descend subfragments; USLCI termination')
    container_frag.term.descend = False
    d = AntelopeTraversalDisclosure(container_frag.traverse('local.uslci.olca'), quiet=quiet, folder_path=folder)
    d.write_excel('simple_uslci_nondescend')

    print('Terminated leaf nodes: USLCI termination')
    container_frag.term.descend = True
    d = AntelopeTraversalDisclosure(container_frag.traverse('breakout uslci'), quiet=quiet, folder_path=folder)
    d.write_excel('simple_uslci_termed')


def large_product_model_mixed_scenarios(cat, fg_name, termination_file, psm=large, quiet=True,
                                        folder=OUTPUT_DIR):
    """
    Demonstrates the disclosure framework for a larger fragment.  Here we are building a container fragment just as
    before, and terminating it to both USLCI and USEEIO.  But we are also terminating the fragment's leaf nodes
    to ELCD, which is incompletely described, so many flows are left un-terminated.

    When we traverse the fragment using one scenario (either USLCI or USEEIO) we see the container fragment handling
    all the unterminated flows from the subfragments.  When we traverse the fragment using just ELCD, we see a lot of
    cutoffs that are not handled at all.  When we traverse the fragment using a mixture of ELCD and the US data, we
    see the terminated leaf nodes going to the ELCD process, and the container fragment picking up the leftovers.

    This function creates four disclosures of the same product model:
     - leaf nodes partially terminated to ELCD
     - container fragment terminated to USEEIO (USLCI is similar)
     - Combined USEEIO and ELCD scenarios, descend
     - Combined USEEIO and ELCD scenarios, non-descend

    :param cat:
    :param fg_name:
    :param termination_file:
    :param psm:
    :param quiet:
    :param folder:
    :return:
    """

    fg = cat.foreground(fg_name, reset=True)  # reset causes reload from
    large_frag = fg.get(psm)

    builder = PsmTerminationBuilder(cat, fg, termination_file, sheet='terminations')

    builder.terminate_leaf_nodes(large_frag, 'local.elcd.3.2', 'ELCD')

    container_frag = builder.build_container(large_frag, 'local.usepa.useeio.1.1')

    print('Generating Disclosures for large product model:\n%s\n' % large_frag)

    print('Leaf terminations: ELCD')
    d = AntelopeTraversalDisclosure(container_frag.traverse('ELCD'), quiet=quiet, folder_path=folder)
    d.write_excel('large_elcd_termed')

    print('Container terminations: USEEIO')
    d = AntelopeTraversalDisclosure(container_frag.traverse('local.usepa.useeio.1.1'), quiet=quiet, folder_path=folder)
    d.write_excel('large_useeio_container')

    print('Mixed scenarios, descend')
    d = AntelopeTraversalDisclosure(container_frag.traverse(('local.usepa.useeio.1.1', 'ELCD')), quiet=quiet,
                                    folder_path=folder)
    d.write_excel('large_mixed_descend')

    # TODO: figure out why this non-descend fragment traversal is failing to disclose
    # print('Mixed scenarios, nondescend')
    # container_frag.term.descend = False
    # d = AntelopeTraversalDisclosure(container_frag.traverse(('local.usepa.useeio.1.1', 'ELCD')), quiet=quiet,
    #                                 folder_path=folder)
    # d.write_excel('large_mixed_nondescend')


def do_epa_study(cat_dir=catalog_dir, fg_name=TRUE_FG_NAME,
                 scratch=False):
    # create and prepare the catalog
    cat = ForegroundCatalog(cat_dir)
    if 'local.uslci.olca' not in cat.references:
        raise NotConfiguredError('Please run python -m unittest to generate background data sources')

    try:
        data_dir = os.path.join(os.getenv('EPA_FOREGROUND'), 'LandingGear')
    except TypeError:
        raise MissingEpaForegroundEnvVar('Please export EPA_FOREGROUND')

    # create and prepare the foreground
    fg = create_annotated_foreground(cat, fg_name, ANNOTATED_XLSX_REL_PATH, scratch=scratch)

    # generate mock price + mass data
    price = cat.query('local.usepa.useeio').get('b0682037-e878-4be4-a63a-a7a81053a691')
    cf_file = os.path.join(cat_dir, fg_name, 'cfs.json')
    mock_inventory_data(fg, price, ANNOTATED_XLSX_REL_PATH, save_file=cf_file)

    if fg.count('fragment') == 0:
        create_epa_psms(fg, data_dir)
        fg.save()

    # generate disclosures
    simple_product_model_disclosures(cat, fg_name, ANNOTATED_XLSX_REL_PATH)
    large_product_model_mixed_scenarios(cat, fg_name, ANNOTATED_XLSX_REL_PATH)


if __name__ == '__main__':
    do_epa_study(scratch=True)
