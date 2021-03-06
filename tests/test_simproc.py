#coding=utf-8
import nose
import driller
import simuvex

import logging
l = logging.getLogger("driller.tests.test_driller_simproc")

import os
bin_location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../binaries'))


def test_simproc_drilling():
    """
    test drilling on the cgc binary palindrome with simprocedures.
    """

    binary = "tests/i386/driller_simproc"
    memcmp = simuvex.procedures.libc___so___6.memcmp.memcmp
    simprocs = {0x8048200: memcmp}
    # fuzzbitmap says every transition is worth satisfying
    d = driller.Driller(os.path.join(bin_location, binary), "A"*0x80, "\xff"*65535, "whatever~", hooks=simprocs)

    new_inputs = d.drill()

    # make sure driller produced a new input which satisfies the memcmp
    password = "the_secret_password_is_here_you_will_never_guess_it_especially_since_it_is_going_to_be_made_lower_case"
    nose.tools.assert_true(any(filter(lambda x: x[1].startswith(password), new_inputs)))


def run_all():
    functions = globals()
    all_functions = dict(filter((lambda (k, v): k.startswith('test_')), functions.items()))
    for f in sorted(all_functions.keys()):
        if hasattr(all_functions[f], '__call__'):
            all_functions[f]()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        globals()['test_' + sys.argv[1]]()
    else:
        run_all()
