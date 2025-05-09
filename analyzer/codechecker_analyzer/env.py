# -------------------------------------------------------------------------
#
#  Part of the CodeChecker project, under the Apache License v2.0 with
#  LLVM Exceptions. See LICENSE for license information.
#  SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
#
# -------------------------------------------------------------------------


import os
import re
import pickle

from codechecker_analyzer import analyzer_context
from codechecker_common.logger import get_logger

LOG = get_logger('system')


def get_log_env(logfile, original_env, use_absolute_ldpreload_path=False):
    """
    Environment for logging. With the ld logger.
    Keep the original environment unmodified as possible.
    Only environment variables required for logging are changed.

    If use_absolute_ldpreload_path is True, use absolute paths in LD_PRELOAD
    instead of relying on LD_LIBRARY_PATH for loading the ldlogger.so library.
    """
    context = analyzer_context.get_context()
    new_env = original_env

    new_env[context.env_var_cc_logger_bin] = context.path_logger_bin

    ldlogger_path = None

    if use_absolute_ldpreload_path:
        LOG.debug("Trying to use absolute paths for ldlogger.so library")
        import platform

        arch_bit = platform.architecture()[0]
        arch_dir = "64bit" if arch_bit == "64bit" else "32bit"
        arch_paths = context.path_logger_lib.split(":")

        for path in arch_paths:
            if path.endswith(arch_dir):
                ldlogger_path = os.path.join(path, context.logger_lib_name)
                break

        if not ldlogger_path and arch_paths:
            LOG.warning(
                ('Could not find current architecture "%s" in list of '
                 'potential paths "%s", falling back to first architecture '
                 'path "%s"!'),
                arch_dir,
                context.path_logger_lib,
                arch_paths[0],
            )
            ldlogger_path = os.path.join(
                arch_paths[0], context.logger_lib_name)

    if use_absolute_ldpreload_path and ldlogger_path:
        LOG.debug(
            'Successfully found absolute path for ldlogger.so library: "%s"',
            ldlogger_path,
        )
        preload_value = ldlogger_path
    else:
        LOG.debug(
            ("Using LD_LIBRARY_PATH environment variable and a relative path "
             "to load ldlogger.so library")
        )
        preload_value = context.logger_lib_name

        try:
            original_ld_library_path = new_env["LD_LIBRARY_PATH"]
            new_env["LD_LIBRARY_PATH"] = (
                context.path_logger_lib + ":" + original_ld_library_path
            )
        except KeyError:
            new_env["LD_LIBRARY_PATH"] = context.path_logger_lib
        LOG.debug(
            'LD_LIBRARY_PATH environment variable set to: "%s"',
            new_env["LD_LIBRARY_PATH"],
        )

    if "LD_PRELOAD" in new_env:
        new_env["LD_PRELOAD"] = new_env["LD_PRELOAD"] + " " + preload_value
    else:
        new_env["LD_PRELOAD"] = preload_value

    LOG.debug('LD_PRELOAD environment variable set to: "%s"',
              new_env["LD_PRELOAD"])

    new_env[context.env_var_cc_logger_file] = logfile

    return new_env


def get_original_env():
    original_env = os.environ
    try:
        original_env_file = os.environ.get('CODECHECKER_ORIGINAL_BUILD_ENV')
        if original_env_file:
            LOG.debug('Loading original build env from: %s', original_env_file)

            with open(original_env_file, 'rb') as env_file:
                original_env = pickle.load(env_file, encoding='utf-8')

    except Exception as ex:
        LOG.warning(str(ex))
        LOG.warning('Failed to get saved original_env ')
        original_env = None
    return original_env


def extend(path_env_extra, ld_lib_path_extra):
    """Extend the checker environment.

    The default environment is extended with the given PATH and
    LD_LIBRARY_PATH values to find tools if they ar not on
    the default places.
    """
    new_env = os.environ.copy()

    if path_env_extra:
        extra_path = ':'.join(path_env_extra)
        LOG.debug(
            'Extending PATH environment variable with: ' + extra_path)

        try:
            new_env['PATH'] = extra_path + ':' + new_env['PATH']
        except KeyError:
            new_env['PATH'] = extra_path

    if ld_lib_path_extra:
        extra_lib = ':'.join(ld_lib_path_extra)
        LOG.debug(
            'Extending LD_LIBRARY_PATH environment variable with: ' +
            extra_lib)
        try:
            original_ld_library_path = new_env['LD_LIBRARY_PATH']
            new_env['LD_LIBRARY_PATH'] = \
                extra_lib + ':' + original_ld_library_path
        except KeyError:
            new_env['LD_LIBRARY_PATH'] = extra_lib

    return new_env


def find_by_regex_in_envpath(pattern, environment):
    """
    Searches for files matching the pattern string in the environment's PATH.
    """

    regex = re.compile(pattern)

    binaries = {}
    for path in environment['PATH'].split(os.pathsep):
        _, _, filenames = next(os.walk(path), ([], [], []))
        for f in filenames:
            if re.match(regex, f):
                if binaries.get(f) is None:
                    binaries[f] = [os.path.join(path, f)]
                else:
                    binaries[f].append(os.path.join(path, f))

    return binaries


def get_binary_in_path(basename_list, versioning_pattern, env):
    """
    Select the most matching binary for the given pattern in the given
    environment. Works well for binaries that contain versioning.
    """

    binaries = find_by_regex_in_envpath(versioning_pattern, env)

    if not binaries:
        return False
    elif len(binaries) == 1:
        # Return the first found (earliest in PATH) binary for the only
        # found binary name group.
        return list(binaries.values())[0][0]
    else:
        keys = list(binaries.keys())
        keys.sort()

        # If one of the base names match, select that version.
        files = None
        for base_key in basename_list:
            # Cannot use set here as it would destroy precendence.
            if base_key in keys:
                files = binaries[base_key]
                break

        if not files:
            # Select the "newest" available version if there are multiple and
            # none of the base names matched.
            files = binaries[keys[-1]]

        # Return the one earliest in PATH.
        return files[0]


def is_analyzer_from_path():
    """ Return True if CC_ANALYZERS_FROM_PATH environment variable is set. """
    analyzers_from_path = os.environ.get('CC_ANALYZERS_FROM_PATH', '').lower()
    if analyzers_from_path in ['yes', '1']:
        return True
    return False


def get_clangsa_plugin_dir():
    """ Return the value of the CC_CLANGSA_PLUGIN_DIR environment variable. """
    return os.environ.get('CC_CLANGSA_PLUGIN_DIR')
