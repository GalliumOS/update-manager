=========================
Computer Janitor plugins
=========================

Computer Janitor supports a plugin architecture which allows you to add
additional ways of identifying and cleaning up *cruft*.  Cruft is anything on
your system that is no longer necessary and can be safely removed.

Identifying cruft is the primary purpose of plugins, and each plugin should
identify exactly one kind of cruft.

The primary interface for this is the `get_cruft()` method on each plugin.
This method should return an iterator over cruft objects, which allows for the
UI to provide useful progress feedback.


Cruft
=====

Cruft objects themselves must implement a specific interface, which is used to
provide information to the user, and to perform the actual clean up
operations.  There is a useful base class that you can start with.

    >>> from janitor.plugincore.cruft import Cruft

You can derive from this base class, but you must implement a couple of
methods, or your cruft class will not be usable.

    >>> cruft = Cruft()
    >>> cruft.get_shortname()
    Traceback (most recent call last):
    ...
    UnimplementedMethod: Unimplemented method: get_shortname
    >>> cruft.cleanup()
    Traceback (most recent call last):
    ...
    UnimplementedMethod: Unimplemented method: cleanup

Here is a cruft subclass that is usable in a plugin.

    >>> class MyCruft(Cruft):
    ...     cruft_id = 1
    ...     def __init__(self):
    ...         self.cleanup_count = 0
    ...         self._prefix = 'MyCruft{:02d}'.format(MyCruft.cruft_id)
    ...         MyCruft.cruft_id += 1
    ...         super(MyCruft, self).__init__()
    ...     def get_shortname(self):
    ...         return 'Example'
    ...     def get_prefix(self):
    ...         return self._prefix
    ...     def cleanup(self):
    ...         self.cleanup_count += 1

Not only do the above methods work, but you can also use a more modern
interface for getting information about the cruft.

    >>> mycruft = MyCruft()
    >>> print(mycruft.shortname)
    Example
    >>> print(mycruft.prefix)
    MyCruft01
    >>> print(mycruft.prefix_description)
    <BLANKLINE>
    >>> print(mycruft.name)
    MyCruft01:Example
    >>> print(mycruft.description)
    <BLANKLINE>
    >>> print(mycruft.disk_usage)
    None
    >>> mycruft.cleanup()
    >>> mycruft.cleanup_count
    1

Cruft objects also have a reasonable repr.

    >>> mycruft
    <MyCruft "MyCruft01:Example">


Plugins
=======

Computer Janitor plugins identify cruft.  They use whatever algorithm
necessary to return iterators over cruft in their `get_cruft()` method.
Plugins must derived from the abstract base class, and must override certain
methods.

    >>> from janitor.plugincore.plugin import Plugin
    >>> Plugin().get_cruft()
    Traceback (most recent call last):
    ...
    UnimplementedMethod: Unimplemented method: cleanup

By subclassing the base class, we can provide a way to find cruft.

    >>> class MyPlugin(Plugin):
    ...     def __init__(self):
    ...         self.post_cleanup_count = 0
    ...         self._my_cruft = [MyCruft()]
    ...         super(MyPlugin, self).__init__()
    ...     def get_cruft(self):
    ...         for cruft in self._my_cruft:
    ...             yield cruft
    ...     def post_cleanup(self):
    ...         self.post_cleanup_count += 1

Now the plugin returns one piece of cruft.

    >>> plugin = MyPlugin()
    >>> for cruft in plugin.cruft:
    ...     print(cruft)
    <MyCruft "MyCruft02:Example">

Plugins are also the way to clean up all their cruft.

    >>> plugin.do_cleanup_cruft()
    >>> for cruft in plugin.cruft:
    ...     print(cruft.name, 'clean ups:', cruft.cleanup_count)
    MyCruft02:Example clean ups: 1

The plugin also gets a chance to perform post-cleanup operations.

    >>> plugin.post_cleanup_count
    1

For historical API reasons, plugins have conditions which are set to the empty
list by default.

    >>> plugin.condition
    []

These conditions can be set.

    >>> plugin.condition = 'my condition'
    >>> print(plugin.condition)
    my condition

Plugins also have optional applications, but by default there is no `app`
attribute (this is for historical API reasons).

    >>> print(plugin.app)
    Traceback (most recent call last):
    ...
    AttributeError: app

The `app` can be set through this historical API.

    >>> plugin.set_application('my application')
    >>> print(plugin.app)
    my application


Plugin manager
==============

The plugin manager is used to find and load plugins.  It searches a list of
directories for files that end in `_plugin.py`.
::

    >>> from janitor.plugincore.testing.helpers import (
    ...     setup_plugins, Application)
    >>> plugin_dir, cleanup = setup_plugins('alpha_plugin.py')
    >>> cleanups.append(cleanup)
    >>> app = Application()

    >>> from janitor.plugincore.manager import PluginManager
    >>> manager = PluginManager(app, [plugin_dir])
    >>> for filename in manager.plugin_files:
    ...     print('plugin file:', filename)
    plugin file: .../alpha_plugin.py

The plugin manager can import each plugin module found and instantiate all
`Plugin` base classes it finds.  After each plugin is found, a callback is
called, which can be used to inform the user of progress.  The arguments of
the callback are:

 * The plugin filename.
 * This plugin number in the total list of plugins found, starting from 0
 * The total number of plugin files to be examined.

    >>> def callback(filename, i, total):
    ...     print('[{:02d}/{:02d}] {}'.format(i, total, filename))

The loaded plugins are cached, so the modules are only imported once.  We'll
use the wildcard condition which matches all plugins.

    >>> plugins = manager.get_plugins(condition='*', callback=callback)
    [00/01] .../alpha_plugin.py
    >>> for plugin in plugins:
    ...     print(plugin)
    <alpha_plugin.AlphaPlugin object at ...>

However, plugins can have conditions and we can use these conditions to get
back a different set of plugins from the manager.

    >>> plugins[0].condition = 'happy'
    >>> len(manager.get_plugins(condition='sad'))
    0
    >>> len(manager.get_plugins(condition='happy'))
    1
