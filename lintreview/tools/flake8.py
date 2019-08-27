import os
import logging
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path

log = logging.getLogger(__name__)


class Flake8(Tool):

    name = 'flake8'

    # see: http://flake8.readthedocs.org/en/latest/config.html
    PYFLAKE_OPTIONS = [
        'exclude',
        'filename',
        'select',
        'ignore',
        'max-line-length',
        'format',
        'max-complexity',
        'snippet',
        'per-file-ignores',
    ]

    def check_dependencies(self):
        """
        See if flake8 is on the PATH
        """
        return in_path('flake8')

    def match_file(self, filename):
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.py'

    def process_files(self, files):
        """
        Run code checks with flake8.
        Only a single process is made for all files
        to save resources.
        """
        # Use relative paths to allow options like '--per-file-ignores' to
        # work. We'll use the 'cwd' arg when running the flake8 subprocess to
        # ensure these relative paths resolve correctly.
        files = [os.path.relpath(f, self.base_path) for f in files]
        log.debug('Processing %s files with %s', files, self.name)
        command = ['flake8']
        for option in self.PYFLAKE_OPTIONS:
            if self.options.get(option):
                command.extend(
                    ['--%(option)s' % {'option': option},
                     self.options.get(option)])

        command += files
        output = run_command(command, split=True, ignore_error=True,
                             cwd=self.base_path)
        if not output:
            log.debug('No flake8 errors found.')
            return False

        for line in output:
            try:
                filename, line, error = self._parse_line(line)
            except ValueError:
                log.warning('Unable to process flake8 output "%s"', line)
                continue

            self.problems.add(filename, line, error)

    def _parse_line(self, line):
        """
        flake8 only generates results as stdout.
        Parse the output for real data.
        """
        parts = line.split(':', 3)
        if len(parts) < 3:
            raise ValueError()
        elif len(parts) == 3:
            message = parts[2].strip()
        else:
            message = parts[3].strip()
        return (parts[0], int(parts[1]), message)
