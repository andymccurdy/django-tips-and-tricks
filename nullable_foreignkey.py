from django.db import connection, models

class NullableForeignKey(models.ForeignKey):
    """
    Prevent the default CASCADE DELETE behavior of normal ForeignKey.
    When an instance pointed to by a NullableForeignKey is deleted,
    the NullableForeignKey field is NULLed rather than the row being deleted.
    """ 
    def __init__(self, *args, **kwargs):
        kwargs['null'] = kwargs['blank'] = True
        super(NullableForeignKey, self).__init__(*args, **kwargs)

    # Monkeypatch the related class's "collect_sub_objects"
    # to not delete this object
    def contribute_to_related_class(self, cls, related):
        super(NullableForeignKey, self).contribute_to_related_class(cls, related)
        _original_csb_attr_name = '_original_collect_sub_objects'
        # define a new "collect_sub_objects" method 
        this_field = self
        def _new_collect_sub_objects(self, *args, **kwargs):
            qn = connection.ops.quote_name
            # find all fields related to the model who's instance is
            # being deleted
            for related in self._meta.get_all_related_objects():
                if isinstance(related.field, this_field.__class__):
                    table = qn(related.model._meta.db_table)
                    column = qn(related.field.column)
                    sql = "UPDATE %s SET %s = NULL WHERE %s = %%s;" % (table, column, column)
                    connection.cursor().execute(sql, [self.pk])

            # Now proceed with collecting sub objects that are still tied via FK
            getattr(self, _original_csb_attr_name)(*args, **kwargs)

        # monkey patch the related classes _collect_sub_objects method.
        # store the original method in an attr named `_original_csb_attr_name`
        if not hasattr(cls, _original_csb_attr_name):
            setattr(cls, _original_csb_attr_name, cls._collect_sub_objects)
            setattr(cls, '_collect_sub_objects', _new_collect_sub_objects)
