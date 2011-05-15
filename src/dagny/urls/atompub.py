import styles
import router


__all__ = ['resources', 'resource']


_router = router.URLRouter(style=styles.AtomPubURLStyle())
resources = _router.resources
resource = _router.resource
