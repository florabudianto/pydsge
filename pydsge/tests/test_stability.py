# This file contains tests to check the stability of the new commit by comparing
# the tutorial output under the new commit to the pickled and stored output of the stable commit

import pickle
import pytest
from pydsge import * # imports eg. the DSGE class and the examples TODO: replace by .__init__ ?
import numpy as np # For np.all()
import logging # for custom error messages

from export_getting_started_to_pkl import * # To get the function: notebook_to_pickable_dict()

@pytest.fixture(scope="module")
def new_output(path = "docs\\getting_started.ipynb"): 
    '''Create dictionary of variables from current state of getting_started. 

    Args:
        path: the path to the tutorial "getting_started.ipynb"
    
    Returns:
        bk_new (dict): A dictionary of the objects and values of the current state of getting_started. The object names are the keys of the dictionary.
    '''
    bk_new = notebook_exec_result_flattened(path)
    bk_new_array = to_ndarray(bk_new)

    return bk_new_array

@pytest.fixture(scope="module")
def stable_output():
    '''Unpickle dictionary of objects and values of stable version.

    Returns:
        bk_restore (dict): A dictionary of the objects and corresponding values of the stable getting_started. The object names are the keys of the dictionary.
    '''
    # Unpickle stable output
    with open('pydsge/tests/resources/getting_started_stable.npz', 'rb') as f:
        npzfile = np.load(f, allow_pickle=False)
        bk_restore = dict(npzfile)

    return bk_restore

@pytest.fixture(scope="module")
def diff(new_output, stable_output):
    '''Get difference between the two dictionaries' keys.
    
    Args:
        new_output (fixture):  A dictionary of the objects and values of the current state of getting_started. The object names are the keys of the dictionary.
        stable_output (fixture): A dictionary of the objects and corresponding values of the stable getting_started. The object names are the keys of the dictionary.
    
    Returns:
        diff (set): A set containing all objects which are contained in only one of the dictionaries.
    '''
    # Load the difference between new_output and stable_output
    diff = stable_output.keys() ^ new_output.keys()

    return diff

@pytest.mark.regression
def test_what_output_is_there(diff):
    '''Check that the stable and the new version contain the same objects (excluding objects from current environment).
    Scenario:
    * Load stable and new output as dictionaries. The objects names are the keys.
    * Convert both dictionaries' keys to sets and find the difference in both directions
    * Combine the differences of both directions in "diff"
    * Check that "diff" is equal to expected difference: empty set.
    '''

#### Print error message in output under "Captured log call " if test fails

    log = logging.getLogger('')
    log.error('\n\nThe test_what_output_is_there Failed. To update the Pickle, run "python pydsge\\tests\export_getting_started_to_pkl.py" in the terminal. \n\n')

    assert diff == set()
    

def nan_undecidable(array):
    return issubclass(np.asarray(array).dtype.type, str) or np.asarray(array).dtype.hasobject


def array_equal(a1, a2):
    if nan_undecidable(a1) or nan_undecidable(a2):
        return np.array_equal(a1, a2, equal_nan=False)
    else:
        return np.array_equal(a1, a2, equal_nan=True)

# @pytest.mark.parametrize("") TODO: don't parametrize  on inputs, but for different tutorials??
@pytest.mark.regression
def test_content_of_outputs(new_output, stable_output, diff):
    '''Check that the objects of the stable and the new version contain the same values
    Scenario:
    * Load stable and new output as dictionaries
    * Find set of variables that are shared by both dictionaries
    * For each shared object, check whether the content is exactly identical
    '''
    # Get collection of shared variables to loop over
    error_vars = {"__warningregistry___version"} #Also FX?
    shared_vars = (stable_output.keys() | new_output.keys()) - diff - error_vars

    # Write function for de-nesting
    def get_flat(nested_object):
        '''Applies function recursively until lowest level is reached.'''
        if not np.iterable(nested_object):
            return nested_object
        output = []
        def reemovNestings(l):
            for i in l:
                if type(i).__name__ in ["list", "tuple", "dict", "ndarray"]:
                    reemovNestings(i)
                else:
                    output.append(i)
        reemovNestings(nested_object)
        return output

    log = logging.getLogger('')
    log.error('\n\nThe test_content_of_outputs Failed. To update the Pickle, run "python pydsge\\tests\export_getting_started_to_pkl.py" in the terminal. \n\n')


    # # Loop over shared vars
    # for key in sorted(shared_vars):
    #     print(f"This is shared_key: {key}")
    #     if type(new_output[key]).__name__ == "DataFrame": 
    #         assert new_output[key].equals(stable_output[key]), f"Error with {key}"
    #     #for nested objects
    #     elif key in ["hd"]: #for lists that contain DataFrames
    #         for counter, _ in enumerate(new_output[key]):
    #             assert array_equal(new_output[key][counter], stable_output[key][counter])
    #     elif type(new_output[key]).__name__ in ["list", "dict", "tuple", "ndarray"]: #Checking whether the object is nested
    #         assert array_equal(get_flat(new_output[key]), get_flat(stable_output[key]))
    #     else:
    #         assert array_equal(new_output[key], stable_output[key]), f"Error with {key}" #Use np.all() for arrays

    for key in sorted(shared_vars):
        print(f"This is shared_key: {key}")
        NEW = np.nan_to_num(new_output[key])
        STABLE = np.nan_to_num(stable_output[key])
        if type(NEW).__name__ == "DataFrame": 
            assert NEW.equals(STABLE), f"Error with {key}"
        #############################
        # Dealing with nested objects #
        #############################
        #for nested objects
        elif key in ["hd"]: #for lists that contain DataFrames
            for counter, _ in enumerate(NEW):
                assert np.all(NEW[counter] == STABLE[counter])
        elif type(NEW).__name__ in ["list", "dict", "tuple", "ndarray"]: #Checking whether the object is nested
            assert get_flat(NEW) == get_flat(STABLE)
        else:
            assert np.all(NEW == STABLE), f"Error with {key}" #Use np.all() for arrays