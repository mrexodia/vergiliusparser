from depgraph import Dataset, buildmanager

# Define Datasets
# Use an optional keyword `tool` to provide a key instructing our build tool
# how to assemble this product. Here we've used strings, but another pattern
# would be to provide a callback function
R0 = Dataset("data/raw0", tool="read_csv")
R1 = Dataset("data/raw1", tool="read_csv")
R2 = Dataset("data/raw2", tool="database_query")
R3 = Dataset("data/raw3", tool="read_hdf")

DA0 = Dataset("step1/da0", tool="merge_fish_counts")
DA1 = Dataset("step1/da1", tool="process_filter")

DB0 = Dataset("step2/db0", tool="join_counts")
DB1 = Dataset("step2/db1", tool="join_by_date")

DC0 = Dataset("results/dc0", tool="merge_model_obs")
DC1 = Dataset("results/dc1", tool="compute_uncertainty")
DC2 = Dataset("results/dc2", tool="make_plots")

# Declare dependency relationships so that depgraph and determine the order of
# the build
DA0.dependson(R0, R1)
DA1.dependson(R2)
DB0.dependson(DA0, DA1)
DB1.dependson(DA1, R3)
DC0.dependson(DB0, DB1)
DC1.dependson(DB1)
DC2.dependson(DB1)

# Option 1:
# Define a function that builds individual dependencies. The *buildmanager*
# decorator transforms it into a loop that builds all dependencies above a
# target
@buildmanager
def batchbuilder(dependency, reason):
    print dependency.name, reason
    return 0

roots = DC0.roots()
for root in roots:
    print root.name
batchbuilder(DC0)
print ""

# Option 2:
# Implement the build loop manually
from depgraph import buildall

def build(dependency, reason):
    # This may have the same logic as `batchbuilder` above, but we
    # will call it directly rather than wrapping it in @buildmanager
    # [....]
    return 0

for stage in buildall(DC1):

    # A build stage is a list of dependencies whose own dependencies are met and
    # that are independent, i.e. they can be built in parallel

    for dep, reason in stage:

        # Each target is a dataset with a 'name' attribute and whatever
        # additional keyword arguments where defined with it.
        # The 'reason' is a depgraph.Reason object that codifies why a
        # particular target is necessary (e.g. it's out of date, it's missing
        # and required by a subsequent target, etc.)
        print("Building {0} with {1} because {2}".format(dep.name, dep.tool,
                                                         reason))

        # Call a function or start a subprocess that will result in the
        # target being built and saved to a file
        return_val = build(dep, reason)

        # Perform logging, clean-up, or error handling operations
        # [....]