class ModelBinder(object):
    def bind(self, context):
        pass


class PrimitiveBinder(ModelBinder):
    def bind(self, context):
        if not context.multiple:
            value = context.values.get(context.name)

            if value is None:
                return None

            return context.type(value)

        values = context.values.getlist(context.name)

        if len(values) == 0:
            return None

        ret = []
        for value in values:
            ret.append(context.type(value))
        return ret
