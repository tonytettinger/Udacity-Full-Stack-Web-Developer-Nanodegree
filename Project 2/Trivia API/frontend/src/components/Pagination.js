import React, { Component } from 'react';

class Pagination extends Component {



    render() {

    const { createPagination } = this.props;
      return (
        <div className="pagination-menu">
          {createPagination}
        </div>
      );
    }
  }


export default Pagination;