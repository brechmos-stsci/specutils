import astropy.nddata
from asdf.yamlutil import custom_tree_to_tagged_tree, tagged_tree_to_custom_tree

from ..types import SpecutilsType
from ....spectra import Spectrum1D, SpectrumList


__all__ = ['Spectrum1DType', 'SpectrumListType']


UNCERTAINTY_TYPE_MAPPING = {
    'std': astropy.nddata.StdDevUncertainty,
    'var': astropy.nddata.VarianceUncertainty,
    'ivar': astropy.nddata.InverseVariance,
    'unknown': astropy.nddata.UnknownUncertainty,
}


class Spectrum1DType(SpecutilsType):
    name = 'spectra/spectrum1d'
    types = [Spectrum1D]
    version = '1.0.0'

    @classmethod
    def to_tree(cls, obj, ctx):

        node = {}
        node['flux'] = custom_tree_to_tagged_tree(obj.flux, ctx)
        node['spectral_axis'] = custom_tree_to_tagged_tree(obj.spectral_axis, ctx)
        if obj.uncertainty is not None:
            node['uncertainty'] = {}
            node['uncertainty']['uncertainty_type'] = obj.uncertainty.uncertainty_type
            data = custom_tree_to_tagged_tree(obj.uncertainty.array, ctx)
            node['uncertainty']['data'] = data

        return node

    @classmethod
    def from_tree(cls, tree, ctx):

        flux = tagged_tree_to_custom_tree(tree['flux'], ctx)
        spectral_axis = tagged_tree_to_custom_tree(tree['spectral_axis'], ctx)
        uncertainty = tree.get('uncertainty', None)
        if uncertainty is not None:
            klass = UNCERTAINTY_TYPE_MAPPING[uncertainty['uncertainty_type']]
            data = tagged_tree_to_custom_tree(uncertainty['data'], ctx)
            uncertainty = klass(data)

        return Spectrum1D(flux=flux, spectral_axis=spectral_axis,
                          uncertainty=uncertainty)

    @classmethod
    def assert_equal(cls, old, new):
        from numpy.testing import assert_allclose
        from astropy.tests.helper import quantity_allclose

        assert quantity_allclose(old.flux, new.flux)
        assert quantity_allclose(old.spectral_axis, new.spectral_axis)
        if old.uncertainty is None:
            assert new.uncertainty is None
        else:
            assert old.uncertainty.uncertainty_type == new.uncertainty.uncertainty_type
            assert_allclose(old.uncertainty.array, new.uncertainty.array)



class SpectrumListType(SpecutilsType):
    name = 'spectra/spectrum_list'
    types = [SpectrumList]
    version = '1.0.0'

    @classmethod
    def to_tree(cls, obj, ctx):
        return [custom_tree_to_tagged_tree(spectrum, ctx) for spectrum in obj]

    @classmethod
    def from_tree(cls, tree, ctx):
        spectra = [tagged_tree_to_custom_tree(node, ctx) for node in tree]
        return SpectrumList(spectra)

    @classmethod
    def assert_equal(cls, old, new):
        assert len(old) == len(new)
        for x, y in zip(old, new):
            Spectrum1DType.assert_equal(x, y)
