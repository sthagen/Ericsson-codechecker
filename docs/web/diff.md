# Comparing analysis results (Diff)

## Introduction
In CodeChecker you may compare analysis results either in the command line or in the web UI. With this tool, you can express _pull request analysis_ (did my pull request introduce/fix any bugs?), and _branch history analysis_ (did a change on my branch introduce/fix any bugs?). This document describes different use-cases for how locally stored analysis results, as well as remotely stored analysis results can be compared, and how other components of CodeChecker (source-code suppressions, review status rules, tags) affect the result of this set.

From the outlook, diff sounds like a very simple feature (and it is!), but it also a powerful tool that allows CodeChecker, among other things, to be used as a gating tool. For this reason, you can express rather complicated queries with it using various filters -- this documents intends to help to understand the expected behaviour of diff in these cases as well.

### How diffs work

The term "diff" means the comparison in between the _outstanding_ reports in a "before" (_baseline_) and an "after" (_new_ or newline) analysis sets. Results are displayed in the same 
format as `CodeChecker cmd results`. A report is _outstanding_ if all of the following is true:
* its [detection status](../../web/server/vue-cli/src/assets/userguide/userguide.md#detection-status) is _new_, _reopened_ or _unresolved_,
* its [review status](../../web/server/vue-cli/src/assets/userguide/userguide.md#review-status) is _unreviewed_ or _confirmed_.
In a nutshell, outstanding reports are those that should be fixed: they are either still detected in the codebase, are unreviewed or confirmed to be true positives. Every other report is considered _closed_.

:warning: Note: When comparing timestamps/tags, we check these conditions at the time of the timestamp/tag (see [here](#diff-on-tags-or-timestamps-branch-history-analysis)).

You can compare both local analysis results (see [CodeChecker analyze](../analyzer/user_guide.md#analyze)) and
results stored on the server (see [CodeChecker store](./user_guide.md#store)). In fact, you can compare
local _and_ remote analyses against one other! We call these in order local-local,
remote-remote, and local-remote or remote-local diffs.

### Usages of diff

`diff` is the primary tool to tell if from the "before" set to the "after" set 
* a _new_ outstanding report appeared,
* a report was _resolved_
* a report is still outstanding (_unresolved_).

Generally speaking, diff allows you to express high level source code quality questions:
* Serverless Pull Request Analysis: Both the analysis result of the baseline (e.g. master branch) and the new code (e.g. soon-to-be pull request) is stored in local report folders, which are then compared to find out new/resolved reports.
* Local/Server Pull Request Analysis: The analysis of a new code (e.g. soon-to-be pull request) is stored locally, while the baseline (e.g. master branch) is on the server.
* Server based Pull Request Analysis: Both the analysis result of the baseline (e.g. master branch) and the new code (e.g. pull request) is located on the server.
* Server based branch history analysis: When making changes to a pull request / branch, analyses of the changes can be stored on the same run. This can be used whether a change on the PR/branch fixed or introduced a new bug.
* 
This allows you to add CodeChecker to your CI loops by checking if a patch introduced a new bug, and you can identify if a patch fixed an existing bug.

:warning: Note: When calculating diff results, reports are uniqued. For more information see [analyzer report identification](../analyzer/report_identification.md).

## Diff from the command line interface
<details>
  <summary>
    <tt>$ <b>CodeChecker cmd diff --help</b> (click to expand)</tt>
  </summary>
  
```
usage: CodeChecker cmd diff [-h] [-b BASE_RUNS [BASE_RUNS ...]]
                            [-n NEW_RUNS [NEW_RUNS ...]] [--print-steps]
                            [--uniqueing {on,off}]
                            [--report-hash [REPORT_HASH [REPORT_HASH ...]]]
                            [--review-status [REVIEW_STATUS [REVIEW_STATUS ...]]]
                            [--detection-status [DETECTION_STATUS [DETECTION_STATUS ...]]]
                            [--severity [SEVERITY [SEVERITY ...]]]
                            [--bug-path-length BUG_PATH_LENGTH]
                            [--tag [TAG [TAG ...]]]
                            [--outstanding-reports-date TIMESTAMP]
                            [--file [FILE_PATH [FILE_PATH ...]]]
                            [--checker-name [CHECKER_NAME [CHECKER_NAME ...]]]
                            [--checker-msg [CHECKER_MSG [CHECKER_MSG ...]]]
                            [--analyzer-name [ANALYZER_NAME [ANALYZER_NAME ...]]]
                            [--component [COMPONENT [COMPONENT ...]]]
                            [--detected-at TIMESTAMP] [--fixed-at TIMESTAMP]
                            [--detected-before TIMESTAMP]
                            [--detected-after TIMESTAMP]
                            [--fixed-before TIMESTAMP]
                            [--fixed-after TIMESTAMP] [-s]
                            (--new | --resolved | --unresolved)
                            [--url PRODUCT_URL]
                            [-o {plaintext,rows,table,csv,json,html,gerrit,codeclimate} [{plaintext,rows,table,csv,json,html,gerrit,codeclimate} ...]]
                            [-e EXPORT_DIR] [-c]
                            [--verbose {info,debug_analyzer,debug}]

Compare two analysis runs to show the results that differ between the two.

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_RUNS [BASE_RUNS ...], --basename BASE_RUNS [BASE_RUNS ...]
                        The 'base' (left) side of the difference: these
                        analysis runs are used as the initial state in the
                        comparison. The parameter can be multiple run names
                        (on the remote server), multiple local report
                        directories (result of the analyze command) or
                        baseline files (generated by the 'CodeChecker parse -e
                        baseline' command). In case of run name the the
                        basename can contain * quantifiers which matches any
                        number of characters (zero or more). So if you have
                        run-a-1, run-a-2 and run-b-1 then "run-a*" selects the
                        first two. In case of run names tag labels can also be
                        used separated by a colon (:) character:
                        "run_name:tag_name". A run name containing a literal
                        colon (:) must be escaped: "run\:name".
  -n NEW_RUNS [NEW_RUNS ...], --newname NEW_RUNS [NEW_RUNS ...]
                        The 'new' (right) side of the difference: these
                        analysis runs are compared to the -b/--basename runs.
                        The parameter can be multiple run names (on the remote
                        server), multiple local report directories (result of
                        the analyze command) or baseline files (generated by
                        the 'CodeChecker parse -e baseline' command). In case
                        of run name the newname can contain * quantifiers
                        which matches any number of characters (zero or more).
                        So if you have run-a-1, run-a-2 and run-b-1 then
                        "run-a*" selects the first two. In case of run names
                        tag labels can also be used separated by a colon (:)
                        character: "run_name:tag_name". A run name containing
                        a literal colon (:) must be escaped: "run\:name".
  --print-steps         Print the steps the analyzers took in finding the
                        reported defect.
  -o {plaintext,rows,table,csv,json,html,gerrit,codeclimate} [{plaintext,rows,table,csv,json,html,gerrit,codeclimate} ...], --output {plaintext,rows,table,csv,json,html,gerrit,codeclimate} [{plaintext,rows,table,csv,json,html,gerrit,codeclimate} ...]
                        The output format(s) to use in showing the data.
                        - html: multiple html files will be generated in the
                        export directory.
                        - gerrit: a 'gerrit_review.json' file will be
                        generated in the export directory.
                        - codeclimate: a 'codeclimate_issues.json' file will
                        be generated in the export directory.
                        For the output formats (json, gerrit, codeclimate) if
                        an export directory is set the output files will be
                        generated if not the results are printed to the stdout
                        but only if one format was selected. (default:
                        ['plaintext'])
  -e EXPORT_DIR, --export-dir EXPORT_DIR
                        Store the output in the given folder.
  -c, --clean           Delete output results stored in the output directory.
                        (By default, it would keep output files and overwrites
                        only those that contain any reports).

filter arguments:
  --uniqueing {on,off}  The same bug may appear several times if it is found
                        on different execution paths, i.e. through different
                        function calls. By turning on uniqueing a report
                        appears only once even if it is found on several
                        paths. (default: off)
  --report-hash [REPORT_HASH [REPORT_HASH ...]]
                        Filter results by report hashes.
  --review-status [REVIEW_STATUS [REVIEW_STATUS ...]]
                        Filter results by review statuses.
                        Reports can be assigned a review status of the
                        following values:
                        - Unreviewed: Nobody has seen this report.
                        - Confirmed: This is really a bug.
                        - False positive: This is not a bug.
                        - Intentional: This report is a bug but we don't want
                        to fix it. This can be used only if basename or
                        newname is a run name (on the remote server).
                        (default: ['unreviewed', 'confirmed'])
  --detection-status [DETECTION_STATUS [DETECTION_STATUS ...]]
                        Filter results by detection statuses.
                        The detection status is the latest state of a bug
                        report in a run. When a unique report is first
                        detected it will be marked as New. When the report is
                        stored again with the same run name then the detection
                        status changes to one of the following options:
                        - Resolved: when the bug report can't be found after
                        the subsequent storage.
                        - Unresolved: when the bug report is still among the
                        results after the subsequent storage.
                        - Reopened: when a Resolved bug appears again.
                        - Off: The bug was reported by a checker that was
                        switched off during the last analysis which results
                        were stored.
                        - Unavailable: were reported by a checker that does
                        not exists in the analyzer anymore because it was
                        removed or renamed. This can be used only if basename
                        or newname is a run name (on the remote server).
                        (default: ['new', 'reopened', 'unresolved'])
  --severity [SEVERITY [SEVERITY ...]]
                        Filter results by severities.
  --bug-path-length BUG_PATH_LENGTH
                        Filter results by bug path length. This has the
                        following format:
                        <minimum_bug_path_length>:<maximum_bug_path_length>.
                        Valid values are: "4:10", "4:", ":10"
  --tag [TAG [TAG ...]]
                        Filter results by version tag names. This can be used
                        only if basename or newname is a run name (on the
                        remote server).
  --outstanding-reports-date TIMESTAMP, --open-reports-date TIMESTAMP
                        Get results which were detected BEFORE the given date
                        and NOT FIXED BEFORE the given date. The detection
                        date of a report is the storage date when the report
                        was stored to the server for the first time. The
                        format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).
  --file [FILE_PATH [FILE_PATH ...]]
                        Filter results by file path. The file path can contain
                        multiple * quantifiers which matches any number of
                        characters (zero or more). So if you have /a/x.cpp and
                        /a/y.cpp then "/a/*.cpp" selects both.
  --checker-name [CHECKER_NAME [CHECKER_NAME ...]]
                        Filter results by checker names. The checker name can
                        contain multiple * quantifiers which matches any
                        number of characters (zero or more). So for example
                        "*DeadStores" will matches "deadcode.DeadStores"
  --checker-msg [CHECKER_MSG [CHECKER_MSG ...]]
                        Filter results by checker messages.The checker message
                        can contain multiple * quantifiers which matches any
                        number of characters (zero or more).
  --analyzer-name [ANALYZER_NAME [ANALYZER_NAME ...]]
                        Filter results by analyzer names. The analyzer name
                        can contain multiple * quantifiers which match any
                        number of characters (zero or more). So for example
                        "clang*" will match "clangsa" and "clang-tidy".
  --component [COMPONENT [COMPONENT ...]]
                        Filter results by source components. This can be used
                        only if basename or newname is a run name (on the
                        remote server).
  --detected-at TIMESTAMP
                        DEPRECATED. Use the '--detected-after/--detected-
                        before' options to filter results by detection date.
                        Filter results by fix date (fixed after the given
                        date) if the --detection-status filter option is set
                        only to Resolved otherwise it filters the results by
                        detection date (detected after the given date). The
                        format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).
  --fixed-at TIMESTAMP  DEPRECATED. Use the '--fixed-after/--fixed-before'
                        options to filter results by fix date. Filter results
                        by fix date (fixed before the given date) if the
                        --detection-status filter option is set only to
                        Resolved otherwise it filters the results by detection
                        date (detected before the given date). The format of
                        TIMESTAMP is 'year:month:day:hour:minute:second' (the
                        "time" part can be omitted, in which case midnight
                        (00:00:00) is used).
  --detected-before TIMESTAMP
                        Get results which were detected before the given date.
                        The detection date of a report is the storage date
                        when the report was stored to the server for the first
                        time. The format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).
  --detected-after TIMESTAMP
                        Get results which were detected after the given date.
                        The detection date of a report is the storage date
                        when the report was stored to the server for the first
                        time. The format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).
  --fixed-before TIMESTAMP
                        Get results which were fixed before the given date.
                        The format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).
  --fixed-after TIMESTAMP
                        Get results which were fixed after the given date. The
                        format of TIMESTAMP is
                        'year:month:day:hour:minute:second' (the "time" part
                        can be omitted, in which case midnight (00:00:00) is
                        used).

comparison modes:
  List reports that can be found only in baseline or new runs or in both. False
  positive and intentional reports are considered as resolved, i.e. these are
  excluded from the report set as if they were not reported.

  --new                 Show results that didn't exist in the 'base' but
                        appear in the 'new' run.
  --resolved            Show results that existed in the 'base' but
                        disappeared from the 'new' run.
  --unresolved          Show results that appear in both the 'base' and the
                        'new' run.

common arguments:
  --url PRODUCT_URL     The URL of the product which will be accessed by the
                        client, in the format of
                        '[http[s]://]host:port/Endpoint'. (default:
                        localhost:8001/Default)
  --verbose {info,debug_analyzer,debug}
                        Set verbosity level.

envionment variables:
  CC_REPO_DIR         Root directory of the sources, i.e. the directory where
                      the repository was cloned. Use it when generating gerrit
                      output.
  CC_REPORT_URL       URL where the report can be found. Use it when generating
                      gerrit output.
  CC_CHANGED_FILES    Path of changed files json from Gerrit. Use it when
                      generating gerrit output.

Exit status
------------------------------------------------
0 - No difference between baseline and newrun
1 - CodeChecker error
2 - There is at least one report difference between baseline and newrun

Example scenario: Compare multiple analysis runs
------------------------------------------------
Compare two runs and show results that didn't exist in the 'run1' but appear in
the 'run2' run:
    CodeChecker cmd diff -b run1 -n run2 --new

Compare a remote run with a local report directory and show results that didn't
exist in the remote run 'run1' but appear in the local report directory:
    CodeChecker cmd diff -b run1 -n /my_report_dir --new

Compare two runs and show results that exist in both runs and filter results
by multiple severity values:
    CodeChecker cmd diff -b run1 -n run2 --unresolved --severity high medium

Compare a baseline file (generated by the 'CodeChecker parse -e baseline'
command) and a local report directory and show new results:
    CodeChecker cmd diff -b /reports.baseline -n /my_report_dir --new
```
</details>

Here are some simple examples on the usage of diff from the command line interface:

- Compare locally stored analyses `./my_base_results` and locally stored analysis `./my_updated_results`:
  ```sh
  CodeChecker cmd diff --basename ./my_base_results --newname ./my_updated_results --new
  ```
- Compare remotely stored runs "My Base Results" and "My Updated Results":
  ```sh
  CodeChecker cmd diff --basename "My Base Results" --newname "My Updated Results" --new
  ```
- Compare remotely stored runs against locally stored analyses:
  ```sh
  CodeChecker cmd diff --basename "My Base Results" --newname ./my_updated_results --new
  CodeChecker cmd diff --basename ./my_base_results --newname "My Updated Results" --new
  ```
## Diff through the web GUI

You can also compare runs on the web GUI one [stored](https://github.com/Ericsson/codechecker/blob/master/docs/usage.md#alternative-1-recommended-store-the-results-of-each-commit-in-the-same-run). On the "Run" page, on the right side of each report, you can see square shaped radio buttons. Clicking on the first one places the run into the "baseline" set, and clicking on the second places it in the "newline" set. After selecting at least one run into each set, you can press the "Diff" button in the upper right corner of the "Run" page.

![image](https://github.com/Szelethus/codechecker/assets/23276031/d93d7a73-5071-49df-a00e-5cf932c10c16)

Read more [here](../../web/server/vue-cli/src/assets/userguide/userguide.md#compare-runs).

## Diff Example

In this section, we'll showcase an example in between two [runs](../usage.md#definition-of-run). There is an example for diffing tags and timestamps as well [further down](#diff-on-tags-or-timestamps).

### Setup
Let's assume you have the following C++ code:

```cpp
// example.cpp

int foo(int z)
{
  if (z == 0)
    return 1 / z; // report by core.DivideZero

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}
```
Lets use CodeChecker to analyze this file:
```sh
CodeChecker check -o ./test_report_dir -b "g++ example.cpp -c"
# Alternatively:
CodeChecker log -o compile_command.json -b "g++ example.cpp -c"
CodeChecker analyze -o ./test_report_dir compile_command.json
```
Using the `parse` command we can see that CodeChecker found and stored
2 reports in `./test_report_dir` (showing only a part of the output):
```sh
CodeChecker parse ./test_report_dir
```
```
----==== Checker Statistics ====----
--------------------------------------------------
Checker name        | Severity | Number of reports
--------------------------------------------------
core.DivideZero     | HIGH     |                 1
deadcode.DeadStores | LOW      |                 1
--------------------------------------------------
----=================----
```
:warning: Note: For the sake of simplictiy, we only enabled the Clang Static Analyzer on these analyses using the `--analyzers=clangsa` flag. We chose omit this flag from our examples. Your actual results may also be different depending on the version of your clang binary.

Let's store the results to a running CodeChecker server:
```sh
CodeChecker store -n "Test Run" ./test_report_dir
```
Now let's fix one of the previous warnings in the `foo` function and create a
new function which contains a new warning:
```cpp
// example.cpp

int foo(int z)
{
  if (z != 0)
    return 1 / z; // no reports

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}

void baz(int *p)
{
  if (!p)
    *p = 0; // report by core.NullDereference
}
```
Let's analyze the file again _into a new directory_, and check the results.
```sh
CodeChecker check -o ./test_report_dir_updated -b "g++ example.cpp -c"
# Alternatively:
CodeChecker log -o compile_command.json -b "g++ example.cpp -c"
CodeChecker analyze -o ./test_report_dir_updated compile_command.json
CodeChecker parse ./test_report_dir_updated
```
```
----==== Checker Statistics ====----
---------------------------------------------------
Checker name         | Severity | Number of reports
---------------------------------------------------
deadcode.DeadStores  | LOW      |                 1
core.NullDereference | HIGH     |                 1
---------------------------------------------------
----=================----
```
Let's store the updated results to a running CodeChecker server:
```sh
CodeChecker store -n "Test Run Updated" ./test_report_dir_updated
```
The image below shows the set of outstanding reports in both of these runs. In this example, every report is outstanding. You can see that 3 different checkers made a single report each:
![image](https://github.com/Szelethus/codechecker/assets/23276031/d47c5ca3-8a98-4459-93cd-a5f782a31ef9)

### Using `CodeChecker cmd diff`
* Show outstanding reports that appeared from first analysis to the next (via `--new`):
  * Local-local diff in between `./test_report_dir` to `./test_report_dir_updated/`:
    ```sh
    CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_updated/ --new
    ```
  * Remote-remote diff in between `Test Run` and `Test Run Updated`:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --new
    ```
  * Remote-local or local-remote diff:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname ./test_report_dir_updated/ --new
    CodeChecker cmd diff --basename ./test_report_dir --newname "Test Run Updated" --new
    ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ---------------------------------------------------
  Checker name         | Severity | Number of reports
  ---------------------------------------------------
  core.NullDereference | HIGH     |                 1
  ---------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that disappeared from first analysis to the next (via `--resolved`): 
  * Local-local diff in between `./test_report_dir` to `./test_report_dir_updated/`:
    ```sh
    CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_updated/ --resolved
    ```
  * Remote-remote diff in between `Test Run` and `Test Run Updated`:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --resolved
    ```
  * Remote-local or local-remote diff:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname ./test_report_dir_updated/ --resolved
    CodeChecker cmd diff --basename ./test_report_dir --newname "Test Run Updated" --resolved
    ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ----------------------------------------------
  Checker name    | Severity | Number of reports
  ----------------------------------------------
  core.DivideZero | HIGH     |                 1
  ----------------------------------------------
  ----=================----
  ```
* Show outstanding reports that remained from first analysis to the next (via `--unresolved`): 
  * Local-local diff in between `./test_report_dir` to `./test_report_dir_updated/`:
    ```sh
    CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_updated/ --unresolved
    ```
  * Remote-remote diff in between `Test Run` and `Test Run Updated`:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --unresolved
    ```
  * Remote-local or local-remote diff:
    ```sh
    CodeChecker cmd diff --basename "Test Run" --newname ./test_report_dir_updated/ --unresolved
    CodeChecker cmd diff --basename ./test_report_dir --newname "Test Run Updated" --unresolved
    ```
  Expected output:
  ```sh
  CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_updated/ --unresolved
  ```
  ```
  ----==== Checker Statistics ====----
  --------------------------------------------------
  Checker name        | Severity | Number of reports
  --------------------------------------------------
  deadcode.DeadStores | LOW      |                 1
  --------------------------------------------------
  ----=================----
  ```

### Using the web GUI

Select "Test Run" to be in the "baseline" set by clicking on the left radio button on the right hand side. Select "Test Run Updated" to be in the "newline" set by clicking on the other one. Click on "DIFF" in the upper right corner.

![image](https://github.com/Szelethus/codechecker/assets/23276031/c7a3d57d-79f5-4610-ab74-b9ec9b5a2f76)

In the middle of the image, we can see the list of oustadning reports that appeared from the baseline to the newline. In the bottom left corner, by clicking on the cogwheel next to "Diff type", you can change diff type:

![image](https://github.com/Szelethus/codechecker/assets/23276031/f731b4a2-d49c-4af8-a42f-1b394a3eb8a2)

The list of reports that are no longer outstadning from the baseline to the newline:

![image](https://github.com/Szelethus/codechecker/assets/23276031/e1ff6c1c-ece7-465c-b1e3-d041be518454)

The list of reports that are outstanding in _both_ the baseline and the newline sets:

![image](https://github.com/Szelethus/codechecker/assets/23276031/5d189057-1525-4ca7-814a-ae771289eaa7)

## Diffs and source code suppressions
[Source code suppressions](../analyzer/user_guide.md#suppressing-false-positives-source-code-comments-for-review-status) allow you set the review status of the report. If you change the review status to either _false positive_ or _intentional_, the report will no longer be outstanding in the _context of the run_.

### Example: Setup

Suppose we generate *baseline* results directory `./test_report_dir` and store it with the name `Test Run` the same way as above. However, for the updated run, modify `example.cpp` with a source suppression (as well as a new function with a fault that will be reported by `deadcode.DeadStores` checker):


```cpp
// example.cpp

int foo(int z)
{
  if (z != 0)
    return 1 / z; // no reports

  return 0;
}

int bar(int x)
{
  int y;
  // codechecker_false_positive [all] suppress all checker results
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}

void baz(int *p)
{
  if (!p)
    *p = 0; // report by core.NullDereference
}
```
Lets analyze and store this updated file:

```sh
CodeChecker check -o ./test_report_dir_src_suppressed -b "g++ example.cpp -c"
CodeChecker store -n "Test Run Src Suppressed" ./test_report_dir_src_suppressed
```
In this image, showing the set of oustanding reports in each analysis, you can see that while `deadcode.DeadStores` is still outstanding in `./test_report_dir`, it is no longer outstanding in `./test_report_dir_src_suppressed` as a result of its false positive review status.

![image](https://github.com/Szelethus/codechecker/assets/23276031/e11790b7-9b6c-418e-b217-6d5b00108e26)

:warning: Note: It is possible for a report to not be outstanding in any of the "baseline" or the "newline" sets. This would have happened if we added the source code suppression for the report made by `deadcode.DeadStores` in the baseline as well. Such reports are abscent from the results of diff, regardless of whether `--new`, `--resolved` or `--unresolved` is used.

### Using `CodeChecker cmd diff`
:warning: Note: Below, only local-local diffs are shown, the remote-remote, local-remote/remote-local diffs are analogous to what's shown [above](#using-codechecker-cmd-diff). Also, we only show the invocation from the command line, not the web GUI, which we also displayed [above](#using-the-web-gui). The result of comparing runs on the command line is the same as comparing them on the web GUI. Let us know if you see any divergence!

* Show outstanding reports that appeared from first analysis to the next (via `--new`):
  ```sh
  CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_src_suppressed/ --new
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ---------------------------------------------------
  Checker name         | Severity | Number of reports
  ---------------------------------------------------
  core.NullDereference | HIGH     |                 1
  ---------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that disappeared from first analysis to the next (via `--resolved`): 
  ```sh
  CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_src_suppressed/ --resolved
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  --------------------------------------------------
  Checker name        | Severity | Number of reports
  --------------------------------------------------
  core.DivideZero     | HIGH     |                 1
  deadcode.DeadStores | LOW      |                 1
  --------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that remained from first analysis to the next (via `--unresolved`): 
  ```sh
  CodeChecker cmd diff --basename ./test_report_dir --newname ./test_report_dir_src_suppressed/ --unresolved
  ```
  Expected output (no checkers are seen):
  ```
  ----======== Summary ========----
  ---------------------------------------------
  Number of processed analyzer result files | 0
  Number of analyzer reports                | 0
  ---------------------------------------------
  ----=================----
  ```

## Review status rules and diffs

Similarly to source code suppressions, you can set the review status of reports [on the GUI](../..//web/server/vue-cli/src/assets/userguide/userguide.md#review-status) as well, which will create a review status rule. Unlike source code suppressions, review status rules set the review status for _all reports_ matching that rule (i.e. [having the same hash](../analyzer/report_identification.md)), _regardless_ whether the rule was created before or after the report was stored, making it easy to mark a report false positive in all runs at the same time. Because these rules are stored on the server, **they play no part in local-local diffs as of yet**.

:warning: Note: Review status rules act differently when runs are compared as opposed to when tags or dates are compared (see [below](#diff-on-tags-or-timestamps)).

:warning: Note: If you are trying out with these examples, keep in mind that review status rules are _not_ deleted even if _all reports that it matches_ (by removing some or all runs in a given product) are. You will need to click on "Configuration" in the upper right corner, select "Review Status Rules", where these rules can be removed.

### Example: Setup

Create `example.cpp` the same way as the previous examples:

```cpp
// example.cpp

int foo(int z)
{
  if (z == 0)
    return 1 / z; // report by core.DivideZero

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}
```
Analyze and store it to a running CodeChecker server:
```sh
CodeChecker check -o ./test_report_dir -b "g++ example.cpp -c"
CodeChecker store -n "Test Run" ./test_report_dir
```

Now, navigate to the the web GUI, and create review status rules. Click on "Test Run".

![image](https://github.com/Szelethus/codechecker/assets/23276031/73adda30-7e03-4117-bc1a-ecac9c01a2b1)

Click on the first report, emitted by `deadcode.DeadStores`.

![image](https://github.com/Szelethus/codechecker/assets/23276031/519551df-f182-4350-8acf-d79edf8c00a2)

Set its review status to false positive.

![image](https://github.com/Szelethus/codechecker/assets/23276031/2bde9a6c-2f7b-4a50-a101-06e6766f8ef2)

Now, modify `example.cpp`: fix the `core.DivideZero` error and introduce a null dereference error:

```cpp
// example.cpp

int foo(int z)
{
  if (z != 0)
    return 1 / z; // no reports

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}

void baz(int *p)
{
  if (!p)
    *p = 0; // report by core.NullDereference
}
```
Analyze and store:

```sh
CodeChecker check -o ./test_report_dir_updated -b "g++ example.cpp -c"
CodeChecker store -n "Test Run Updated" ./test_report_dir_updated
```

Looking at the web GUI, you can observe that the report emitted by `deadcode.DeadStores` has a false positive review status, shown by the grey no entry sign :no_entry_sign: in the Review Status column. Note that we cleared the review status filter, which won't list false positive reports by default. Below is the "Reports" view for "Test Run":

![image](https://github.com/Szelethus/codechecker/assets/23276031/3117b9fd-bda0-495f-94a3-1d8843f1c8f5)

Below is the "Reports" view for "Test Run Updated":

![image](https://github.com/Szelethus/codechecker/assets/23276031/97c1bb34-0b2e-4244-ae3c-9cdb7a2ffc9d)

As a result, this report is not outstanding in either of the runs:

![image](https://github.com/Szelethus/codechecker/assets/23276031/9201f853-967b-4d88-a074-7289572c6061)

### Using `CodeChecker cmd diff`
* Show outstanding reports that appeared from first analysis to the next (via `--new`):
  ```sh
  CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --new
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ---------------------------------------------------
  Checker name         | Severity | Number of reports
  ---------------------------------------------------
  core.NullDereference | HIGH     |                 1
  ---------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that disappeared from first analysis to the next (via `--resolved`): 
  ```sh
  CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --resolved
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ----------------------------------------------
  Checker name    | Severity | Number of reports
  ----------------------------------------------
  core.DivideZero | HIGH     |                 1
  ----------------------------------------------
  ----=================----
  ```
* Show outstanding reports that remained from first analysis to the next (via `--unresolved`): 
  ```sh
  CodeChecker cmd diff --basename "Test Run" --newname "Test Run Updated" --unresolved
  ```
  Expected output (no checkers are seen):
  ```
  ----======== Summary ========----
  ---------------------------------------------
  Number of processed analyzer result files | 0
  Number of analyzer reports                | 0
  ---------------------------------------------
  ----=================----
  ```

## Diff on tags or timestamps (_branch history analysis_)

If a run is continously updated with new analysis results, it can store the past report states of all previous analysis executions. This can be useful to analyze how the reports were fixed, classified to false positives, or introduced over the development timeline. You can filter the analysis results or diff results based on which reports were outstanding _before_ a given timestamp. In the below image, on the web GUI, we diff the reports outstanding before the 1st of January, 2023 in "Test Run" against reports  outstanding before the 1st of January, 2023 in "Test Run Updated":

![image](https://github.com/Szelethus/codechecker/assets/23276031/17cc202e-48ab-40ee-a380-dc95a7d0ea41)

You can also name timestamps which we call _tags_. In the below image, the cogwheels were clicked next to "Run/Tag Filter", and then next to "Test Run". There, you can select tags to be put into the baseline set:

![image](https://github.com/Szelethus/codechecker/assets/23276031/4ee5caa8-b7df-452c-8a94-e4c714e69dd3)


Comparing runs and comparing tags/timestamps has a subtle difference:

* For runs, we check whether a report is outstanding _at the time of the query_. This means, as seen [in a previous example](diff.md#example-setup-1), if you store a report, _and then_ set a false positive review status rule for it, _and then_ diff this _run_ against another, the report **will not be** present in the run's outstanding reports set. 
* For tags/timestamps, we check whether a report is outstanding _before that specific tag/timestamp_. This means that if you store a report under `tag1`, _and then_ set a false positive review status rule for it, _and then_ diff this _tag_ against another, the report **will be** present in the tag's outstanding report set. This also implies that **we ignore the detection status of the report, as it always describes its current status (which may differ from the timestamp in the query)**.

To summarize, at timestamp/tag T, a report is outstanding if
* it was detected before or at T,
* its detection status was _new_, _reopened_ or _unresolved_ at T,
* its review status is _unreviewed_ or _confirmed_ at T.

:warning: Note: Tags are created when the report is stored. As a result, you can diff a local analysis directory against a remote tag, but there are no "local tags".

:no_entry: Note: You can compare tags through the command line and the web GUI as well. Currently, you can only compare timestamps on the web GUI.

:no_entry: Note: We are aware of a bug where comparing tags older than the last may yield incorrect results in specific circumstances. It only stores the date when a report was first detected in a run and the date when it was closed. If the report is closed and opened several times, it will only remember the first detection date, and the last close date. So CodeChecker assumes the worst: it regards a report which is on/and/off as it was always there until it is finally fixed. In practice this means, that when you compare the run state at two past tags (after a report detection, but before final fix), a reopened report will be considered as always outstanding after first detection and not appear as new report in the diff. You can read more about this in [issue](https://github.com/Ericsson/codechecker/issues/3884) in section "Tag diffs -> Local-Remote -> the footnote with the double asterisk (**)".

### Example setup

Create `example.cpp` the same way as the previous examples:

```cpp
// example.cpp

int foo(int z)
{
  if (z == 0)
    return 1 / z; // report by core.DivideZero

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}
```
Analyze and store it to a running CodeChecker server but under tag `tag1`:
```sh
CodeChecker check -o ./test_report_dir -b "g++ example.cpp -c"
CodeChecker store -n "Test Run" ./test_report_dir --tag tag1
```

Now, navigate to the the web GUI, and create review status rules. Click on "Test Run".

![image](https://github.com/Szelethus/codechecker/assets/23276031/73adda30-7e03-4117-bc1a-ecac9c01a2b1)

Click on the first report, emitted by `deadcode.DeadStores`.

![image](https://github.com/Szelethus/codechecker/assets/23276031/519551df-f182-4350-8acf-d79edf8c00a2)

Set its review status to false positive.

![image](https://github.com/Szelethus/codechecker/assets/23276031/2bde9a6c-2f7b-4a50-a101-06e6766f8ef2)

Now, modify `example.cpp`: fix the `core.DivideZero` error and introduce a null dereference error:

```cpp
// example.cpp

int foo(int z)
{
  if (z != 0)
    return 1 / z; // no reports

  return 0;
}

int bar(int x)
{
  int y;
  y = x % 2; // report by deadcode.DeadStores

  return x % 2;
}

void baz(int *p)
{
  if (!p)
    *p = 0; // report by core.NullDereference
}
```
Analyze and store results under tag `tag2`. **Note** that we store under the same run name, but with a different tag:

```sh
CodeChecker check -o ./test_report_dir_updated -b "g++ example.cpp -c"
CodeChecker store -n "Test Run" ./test_report_dir_updated --tag tag2
```

Looking at the Run view, when we click on the little arrow to the left of "Test Run", we can see the two analyses under different tags:

![image](https://github.com/Szelethus/codechecker/assets/23276031/98497530-fdd4-439d-8c64-61af1e06f1f2)

Given the chronological order that we first analyzer and stored `tag1`, _and then_ set a false positive review status rule to `deadcode.DeadStores`, _and then_ analyzed and stored `tag2`, the `deadcode.DeadStores` report will be outstanding in `tag1`, but not in `tag2`:

![image](https://github.com/Szelethus/codechecker/assets/23276031/39e738ab-1eba-416a-a1f4-0ba4834b5e95)

### Using `CodeChecker cmd diff`
* Show outstanding reports that appeared from first analysis to the next (via `--new`):
  ```sh
  CodeChecker cmd diff --basename "Test Run":tag1 --newname "Test Run":tag2 --new
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  ---------------------------------------------------
  Checker name         | Severity | Number of reports
  ---------------------------------------------------
  core.NullDereference | HIGH     |                 1
  ---------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that disappeared from first analysis to the next (via `--resolved`): 
  ```sh
  CodeChecker cmd diff --basename "Test Run":tag1 --newname "Test Run":tag2 --resolved
  ```
  Expected output:
  ```
  ----==== Checker Statistics ====----
  --------------------------------------------------
  Checker name        | Severity | Number of reports
  --------------------------------------------------
  core.DivideZero     | HIGH     |                 1
  deadcode.DeadStores | LOW      |                 1
  --------------------------------------------------
  ----=================----
  ```
* Show outstanding reports that remained from first analysis to the next (via `--unresolved`): 
  ```sh
  CodeChecker cmd diff --basename "Test Run":tag1 --newname "Test Run":tag2 --unresolved
  ```
  Expected output (no checkers are seen):
  ```
  ----======== Summary ========----
  ---------------------------------------------
  Number of processed analyzer result files | 0
  Number of analyzer reports                | 0
  ---------------------------------------------
  ----=================----
  ```

### Using the web GUI:

After clicking the dropdown button next to "Test Run", select tags to be put in the baseline and newline sets. Then, click the "DIFF" button the upper left corner. You can interpret the results the same way as in the [first example](#using-the-web-gui).

![image](https://github.com/Szelethus/codechecker/assets/23276031/7c464eca-5b19-491c-889f-c489eebfffd5)
